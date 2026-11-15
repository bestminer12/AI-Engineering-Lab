from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
import requests
from app.vector_store import search_documents
from app.auth import get_current_user
from pydantic import BaseModel, ConfigDict
from app.security_logger import logger
from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

app = FastAPI(title="GenAI Security Assessment Lab")

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError
):
    for error in exc.errors():
        if (
            error.get("type") == "extra_forbidden"
            and tuple(error.get("loc", ())) == ("body", "role")
        ):
            logger.warning(
                "ROLE_ESCALATION_ATTEMPT "
                "reason=UNEXPECTED_ROLE_FIELD"
            )

    return JSONResponse(
        status_code=422,
        content={
            "detail": [
                {
                    "type": error.get("type"),
                    "loc": list(error.get("loc", ())),
                    "msg": error.get("msg")
                }
                for error in exc.errors()
            ]
        }
    )


class ChatRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    question: str


@app.get("/")
def home():
    return {"message": "GenAI Security API is running"}


@app.post("/chat")
def chat(
    request: ChatRequest,
    current_user: dict = Depends(get_current_user)
    ):
    url = "http://localhost:11434/api/chat"


    documents = search_documents(
    request.question,
    role=current_user["role"]
    )   

    #print("검색된 문서:", documents)  # ← 이 줄만 추가!
    document = "\n\n".join(documents)

    data = {
        "model": "qwen2.5:1.5b",
        "messages": [
            {
                "role": "system",
                "content": (
                    "Always answer in Korean. "
                    "Answer questions using only the company policy "
                    "provided below. If the answer is not in the policy, "
                    "say you do not know.\n\n"
                    f"Company policy:\n{document}"
                )
            },
            {
                "role": "user",
                "content": request.question
            }
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

