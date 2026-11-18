
from langchain_ollama import ChatOllama
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import StateGraph, START, END, MessagesState
from langgraph.prebuilt import ToolNode, tools_condition


# 1. Test tool
@tool
def aggregate_auth_failures(user_name: str) -> str:
    """Count failed login attempts for a specified user."""

    print(f"[TOOL EXECUTED] aggregate_auth_failures: {user_name}")

    # Fixed test result; no OpenSearch query yet.
    if user_name == "alice":
        return "User alice has 8 failed login attempts."

    return f"No test data available for {user_name}."


# 2. Initialize LLM
llm = ChatOllama(
    model="qwen2.5:1.5b",
    temperature=0,
)

tools = [aggregate_auth_failures]
llm_with_tools = llm.bind_tools(tools)


# 3. Agent node
def agent_node(state: MessagesState):
    response = llm_with_tools.invoke(state["messages"])
    return {"messages": [response]}


# 4. Build LangGraph
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


# 5. Execute test
if __name__ == "__main__":
    result = app.invoke(
        {
            "messages": [
                SystemMessage(
                    content=(
                        "You are a security investigation assistant. "
                        "Use the available tool to answer the user's question. "
                        "Do not invent security log data."
                    )
                ),
                HumanMessage(
                    content=(
                        "Count the failed login attempts for user alice. "
                        "Use the available tool."
                    )
                ),
            ]
        },
        config={"recursion_limit": 6},
    )

    print("\n=== Execution History ===")

    for message in result["messages"]:
        print(f"Type: {message.type}")

        if getattr(message, "tool_calls", None):
            print("Tool calls:", message.tool_calls)

        if message.type == "tool":
            print("Tool result:", message.content)

    print("\n=== Final Answer ===")
    print(result["messages"][-1].content)
