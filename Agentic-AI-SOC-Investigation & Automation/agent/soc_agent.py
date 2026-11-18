
import json
import sys
from pathlib import Path

from langchain_ollama import ChatOllama
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import StateGraph, START, END, MessagesState
from langgraph.prebuilt import ToolNode, tools_condition

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

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
tool_call_count = 0


@tool
def search_security_logs(user_name: str) -> str:
    """Search individual security events for a user."""

    global tool_call_count
    tool_call_count += 1

    if tool_call_count > MAX_TOOL_CALLS:
        return json.dumps({"error": "Tool call limit exceeded"})

    if not user_name or not user_name.strip():
        return json.dumps({"error": "Invalid user_name"})

    print(f"[TOOL EXECUTED] search_security_logs: {user_name}")

    results = query_logs(
        user_name=user_name,
        start_time=START_TIME,
        end_time=END_TIME,
        size=20,
    )

    return json.dumps(results, ensure_ascii=False)


@tool
def aggregate_auth_failures(user_name: str) -> str:
    """Count failed login attempts for a user."""

    global tool_call_count
    tool_call_count += 1

    if tool_call_count > MAX_TOOL_CALLS:
        return json.dumps({"error": "Tool call limit exceeded"})

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

    global tool_call_count
    tool_call_count += 1

    if tool_call_count > MAX_TOOL_CALLS:
        return json.dumps({"error": "Tool call limit exceeded"})

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

    global tool_call_count
    tool_call_count += 1

    if tool_call_count > MAX_TOOL_CALLS:
        return json.dumps({"error": "Tool call limit exceeded"})

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
)

tools = [
    search_security_logs,
    aggregate_auth_failures,
    correlate_auth_events,
    build_event_timeline,
]

llm_with_tools = llm.bind_tools(tools)


def agent_node(state: MessagesState):
    response = llm_with_tools.invoke(state["messages"])
    return {"messages": [response]}


graph = StateGraph(MessagesState)

graph.add_node("agent", agent_node)
graph.add_node("tools", ToolNode(tools))

graph.add_edge(START, "agent")

graph.add_conditional_edges(
    "agent",
    tools_condition,
    {
        "tools": "tools",
        "__end__": END,
    },
)

graph.add_edge("tools", "agent")

app = graph.compile()


if __name__ == "__main__":
    tool_call_count = 0

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
                        "Count failed login attempts, "
                        "check for suspicious authentication correlations, "
                        "and build an event timeline. "
                        "Use the appropriate tools."
                    )
                ),
            ]
        },
        config={"recursion_limit": 12},
    )

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

