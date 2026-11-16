
import requests

url = "http://localhost:11434/api/chat"

messages = [
    {
        "role": "system",
        "content": "Always answer in Korean."
    }
]

while True:
    question = input("\nAI에게 질문하세요 (종료: exit): ")

    if question.lower() == "exit":
        print("챗봇을 종료합니다.")
        break

    messages.append({
        "role": "user",
        "content": question
    })

    data = {
        "model": "qwen2.5:1.5b",
        "messages": messages,
        "stream": False
    }

    try:
        response = requests.post(url, json=data, timeout=120)
        response.raise_for_status()

        result = response.json()
        answer = result["message"]["content"]

        print("\nAI:", answer)

        messages.append({
            "role": "assistant",
            "content": answer
        })

    except requests.RequestException as error:
        messages.pop()
        print("API 요청 오류:", error)
