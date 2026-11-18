
from langchain_ollama import ChatOllama
from langchain_core.tools import tool

MODEL_NAME = "qwen2.5:1.5b"


@tool
def search_security_logs(user_name: str) -> str:
    """Search individual security log events for a user."""
    return f"Search requested for {user_name}"


@tool
def aggregate_auth_failures(user_name: str) -> str:
    """Count failed login attempts for a user."""
    return f"Aggregation requested for {user_name}"


llm = ChatOllama(
    model=MODEL_NAME,
    temperature=0,
)

tools = [
    search_security_logs,
    aggregate_auth_failures,
]

llm_with_tools = llm.bind_tools(tools)

response = llm_with_tools.invoke(
    "Count the failed login attempts for user alice. "
    "Use the appropriate tool."
)

print("LLM Response:")
print(response.content)

print("\nTool Calls:")
print(response.tool_calls)

print("\nTest Result:")

if response.tool_calls:
    for call in response.tool_calls:
        print("Tool:", call["name"])
        print("Arguments:", call["args"])

    if (
        len(response.tool_calls) == 1
        and response.tool_calls[0]["name"]
        == "aggregate_auth_failures"
        and response.tool_calls[0]["args"].get("user_name")
        == "alice"
    ):
        print("PASS: Correct tool selected")
    else:
        print("FAIL: Unexpected tool or arguments")
else:
    print("FAIL: No tool call generated")
