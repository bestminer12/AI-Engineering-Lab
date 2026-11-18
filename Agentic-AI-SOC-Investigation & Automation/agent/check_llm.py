
from langchain_ollama import ChatOllama

MODEL_NAME = "qwen2.5:1.5b"

llm = ChatOllama(
    model=MODEL_NAME,
    temperature=0,
)

response = llm.invoke(
    "What is the purpose of a Security Operations Center? "
    "Answer in one short sentence."
)

print("LLM Response:")
print(response.content)
