
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests

app = FastAPI(title="GenAI Security Assessment Lab")


class ChatRequest(BaseModel):
    question: str


@app.get("/")
def home():
    return {"message": "GenAI Security API is running"}


@app.post("/chat")
def chat(request: ChatRequest):
    url = "http://localhost:11434/api/chat"

    data = {
        "model": "qwen2.5:1.5b",
        "messages": [
            {"role": "system", "content": "Always answer in Korean."},
            {"role": "user", "content": request.question}
        ],
        "stream": False
    }

    try:
        response = requests.post(url, json=data, timeout=120)
        response.raise_for_status()

        result = response.json()
        answer = result["message"]["content"]

        return {"answer": answer}

    except (requests.RequestException, ValueError, KeyError, TypeError):
        raise HTTPException(
            status_code=502,
            detail="LLM 서버 요청 또는 응답 처리에 실패했습니다."
        )
