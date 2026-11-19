
import json
import sys
from pathlib import Path
import time


from typing import Annotated, TypedDict
from langgraph.graph.message import add_messages

from langchain_ollama import ChatOllama
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage
from langgraph.graph import StateGraph, START, END, MessagesState
from langgraph.prebuilt import ToolNode, tools_condition

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from security.sensitive_data_filter import mask_sensitive_data
from run_investigation import run_investigation

from tools.generate_investigation_report import (
    generate_investigation_report as create_report,
)

from tools.search_security_logs import search_security_logs as query_logs
from tools.aggregate_auth_failures import aggregate_auth_failures as query_failures
from tools.correlate_auth_events import correlate_auth_events as query_correlations
from tools.build_event_timeline import build_event_timeline as query_timeline

START_TIME = "2026-11-17T00:00:00Z"
END_TIME = "2026-11-17T01:00:00Z"

# Lab safety limits
MAX_TOOL_CALLS = 4

class SOCState(TypedDict):
    messages: Annotated[list, add_messages]
    tool_call_count: int


def sanitize_security_logs(results):
    """Keep only approved security event fields."""

    allowed_fields = {
        "@timestamp",
        "timestamp",
        "event_id",
        "event",
        "user",
        "user_name",
        "source",
        "source_ip",
        "outcome",
        "action",
    }

    nested_allowed_fields = {
        "event": {"action", "outcome", "category", "type"},
        "user": {"name"},
        "source": {"ip"},
    }

    def sanitize(value, parent=None):
        if isinstance(value, list):
            return [sanitize(item, parent) for item in value]

        if isinstance(value, dict):
            permitted = nested_allowed_fields.get(parent, allowed_fields)

            return {
                key: sanitize(item, key)
                for key, item in value.items()
                if key in permitted
            }

        return value

    return sanitize(results)

@tool
def search_security_logs(user_name: str) -> str:
    """Search individual security events for a user."""

    if not user_name or not user_name.strip():
        return json.dumps({"error": "Invalid user_name"})

    print(f"[TOOL EXECUTED] search_security_logs: {user_name}")

    # 1. OpenSearch에서 로그 조회
    results = query_logs(
        user_name=user_name,
        start_time=START_TIME,
        end_time=END_TIME,
        size=20,
    )

    # 1. 허용된 로그 필드만 선택
    safe_results = sanitize_security_logs(results)

    # 2. 남아 있는 민감정보 마스킹
    safe_results = mask_sensitive_data(safe_results)

    # 3. 필터링된 로그 확인 (테스트용)
    print(
        "[SANITIZED LOGS]",
        json.dumps(
            safe_results[:2] if isinstance(safe_results, list) else safe_results,
            ensure_ascii=False,
            indent=2,
        ),
    )

    # 4. 필터링된 결과를 LangGraph에 반환
    return json.dumps(safe_results, ensure_ascii=False)

@tool
def aggregate_auth_failures(user_name: str) -> str:
    """Count failed login attempts for a user."""


    if not user_name or not user_name.strip():
        return json.dumps({"error": "Invalid user_name"})

    print(f"[TOOL EXECUTED] aggregate_auth_failures: {user_name}")

    results = query_failures(
        start_time=START_TIME,
        end_time=END_TIME,
        min_failures=1,
    )

    filtered = [
        item for item in results
        if item["user"] == user_name
    ]

    return json.dumps(filtered, ensure_ascii=False)


@tool
def correlate_auth_events(user_name: str) -> str:
    """Find suspicious authentication correlations for a user."""


    if not user_name or not user_name.strip():
        return json.dumps({"error": "Invalid user_name"})

    print(f"[TOOL EXECUTED] correlate_auth_events: {user_name}")

    results = query_correlations(
        start_time=START_TIME,
        end_time=END_TIME,
        failure_threshold=3,
        window_minutes=15,
    )

    filtered = [
        item for item in results
        if item["user"] == user_name
    ]

    return json.dumps(filtered, ensure_ascii=False)


@tool
def build_event_timeline(user_name: str) -> str:
    """Build a chronological security event timeline for a user."""


    if not user_name or not user_name.strip():
        return json.dumps({"error": "Invalid user_name"})

    print(f"[TOOL EXECUTED] build_event_timeline: {user_name}")

    results = query_timeline(
        user_name=user_name,
        start_time=START_TIME,
        end_time=END_TIME,
        size=100,
    )

    return json.dumps(results, ensure_ascii=False)


llm = ChatOllama(
    model="qwen2.5:1.5b",
    temperature=0,
    base_url="http://localhost:11434",
    client_kwargs={"timeout": 120.0},
)

tools = [
    search_security_logs,
    aggregate_auth_failures,
    correlate_auth_events,
    build_event_timeline,
]

llm_with_tools = llm.bind_tools(tools)


def agent_node(state: SOCState):
    print("[DEBUG] Ollama request started", flush=True)

    start = time.perf_counter()

    response = llm_with_tools.invoke(state["messages"])

    elapsed = time.perf_counter() - start

    print(f"[DEBUG] Ollama response received: {elapsed:.2f}s", flush=True)

    return {"messages": [response]}


def tool_node_with_limit(state: SOCState):
    last_message = state["messages"][-1]
    requested_calls = len(last_message.tool_calls)

    current_count = state.get("tool_call_count", 0)

    if current_count + requested_calls > MAX_TOOL_CALLS:
        print("[BLOCKED] Tool call limit exceeded")

        return {
            "messages": [
                ToolMessage(
                    content="Tool call limit exceeded",
                    tool_call_id=call["id"],
                    name=call["name"],
                    status="error",
                )
                for call in last_message.tool_calls
            ],
            "tool_call_count": current_count,
        }

    result = ToolNode(tools).invoke({
        "messages": state["messages"]
    })

    return {
        "messages": result["messages"],
        "tool_call_count": current_count + requested_calls,
    }


def route_after_agent(state: SOCState):
    last_message = state["messages"][-1]

    if not last_message.tool_calls:
        return END

    if state.get("tool_call_count", 0) >= MAX_TOOL_CALLS:
        return "limit_reached"

    return "tools"


def limit_reached_node(state: SOCState):
    print("[BLOCKED] Maximum tool calls reached")
    return {}


graph = StateGraph(SOCState)

graph.add_node("agent", agent_node)
graph.add_node("tools", tool_node_with_limit)
graph.add_node("limit_reached", limit_reached_node)

graph.add_edge(START, "agent")

graph.add_conditional_edges(
    "agent",
    route_after_agent,
    {
        "tools": "tools",
        "limit_reached": "limit_reached",
        END: END,
    },
)

graph.add_edge("tools", "agent")
graph.add_edge("limit_reached", END)

app = graph.compile()


def main():
    benchmark_start = time.perf_counter()

    result = app.invoke(
        {
            "messages": [
                SystemMessage(
                    content=(
                        "You are a SOC investigation assistant. "
                        "Investigate using available tools. "
                        "Use tools sequentially when needed. "
                        "Do not invent log data. "
                        "Only report findings supported by tool results. "
                        "Stop after collecting sufficient evidence."
                    )
                ),
                HumanMessage(
                    content=(
                        "Investigate user alice. "
                        "Use search_security_logs to retrieve her security events."
                    )
                ),
            ],
            "tool_call_count": 0,
        },
        config={"recursion_limit": 12},
    )

    print("\n=== Tool Call Limit Verification ===")
    print("Executed tool calls:", result["tool_call_count"])
    print("Maximum allowed:", MAX_TOOL_CALLS)

    assert result["tool_call_count"] <= MAX_TOOL_CALLS

    print("[PASS] Tool call count within limit")
    print("\n=== Execution History ===")

    for message in result["messages"]:
        if getattr(message, "tool_calls", None):
            for call in message.tool_calls:
                print("Tool selected:", call["name"])

        if message.type == "tool":
            print("Tool result received:", message.name)

    print("\n=== Final Answer ===")
    print(result["messages"][-1].content)


    print("\n=== Verified Investigation Report ===")

    # Use actual OpenSearch results, not LLM-generated evidence.
    findings = query_correlations(
        start_time=START_TIME,
        end_time=END_TIME,
        failure_threshold=3,
        window_minutes=15,
    )

    timeline = query_timeline(
        user_name="alice",
        start_time=START_TIME,
        end_time=END_TIME,
        size=100,
    )

    report = create_report(
        user_name="alice",
        start_time=START_TIME,
        end_time=END_TIME,
        findings=findings,
        timeline=timeline,
    )

    print(json.dumps(report, indent=2, ensure_ascii=False))

    print("\n=== Report Verification ===")
    print("Report type:", report.get("report_type"))
    print("Investigation user:", report.get("investigation", {}).get("user"))
    print("Summary:", report.get("summary"))

    # Phase 6-3: Automated Investigation & Alert Pipeline
    print("\n=== Automated Investigation & Alert Pipeline ===")
    run_investigation(user_name="alice", report=report)

    benchmark_elapsed = time.perf_counter() - benchmark_start

    print("\n=== Agent Benchmark Results ===")
    print(f"Total elapsed: {benchmark_elapsed:.2f}s")

if __name__ == "__main__":
    try:
        main()

    except Exception as exc:
        print(
            f"[ERROR] Agent execution failed: {type(exc).__name__}: {exc}",
            flush=True,
        )
        print(
            "[ABORTED] Agent investigation stopped.",
            flush=True,
        )
        raise SystemExit(1)