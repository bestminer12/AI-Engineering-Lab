from langchain_core.messages import AIMessage
from langgraph.graph import StateGraph, START, END, MessagesState
from langgraph.prebuilt import ToolNode

from soc_agent import tools

# Register only approved tools
graph = StateGraph(MessagesState)

graph.add_node("tools", ToolNode(tools))
graph.add_edge(START, "tools")
graph.add_edge("tools", END)

app = graph.compile()

# Simulate an unauthorized LLM tool request
test_message = AIMessage(
    content="",
    tool_calls=[
        {
            "name": "delete_security_logs",
            "args": {},
            "id": "test_unauthorized_001",
            "type": "tool_call",
        }
    ],
)

result = app.invoke({
    "messages": [test_message]
})

for message in result["messages"]:
    if message.type == "tool":
        print("Tool:", message.name)
        print("Result:", message.content)

tool_results = [
    message for message in result["messages"]
    if message.type == "tool"
]

assert len(tool_results) == 1
assert tool_results[0].status == "error"

print("[PASS] Unauthorized tool execution blocked")