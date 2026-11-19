from langchain_core.messages import AIMessage

from soc_agent import (
    MAX_TOOL_CALLS,
    tool_node_with_limit,
)

test_message = AIMessage(
    content="",
    tool_calls=[
        {
            "name": "search_security_logs",
            "args": {"user_name": "alice"},
            "id": "test_call_005",
            "type": "tool_call",
        }
    ],
)

# 이미 4번 호출한 상태를 가정
state = {
    "messages": [test_message],
    "tool_call_count": 4,
}

result = tool_node_with_limit(state)

print("Current count:", result["tool_call_count"])
print("Tool response:", result["messages"][0].content)

assert result["tool_call_count"] == MAX_TOOL_CALLS
assert result["messages"][0].status == "error"
assert "Tool call limit exceeded" in result["messages"][0].content

print("[PASS] Fifth tool call blocked")