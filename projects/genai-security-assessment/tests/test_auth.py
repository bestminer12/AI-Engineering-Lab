from fastapi.testclient import TestClient
from app.main import app
from app.auth import get_current_user
from app.vector_store import search_documents
import os
from unittest.mock import Mock
import app.main as main_module


client = TestClient(app)


def test_missing_api_key():
    response = client.post(
        "/chat",
        json={"question": "비밀번호 정책은?"}
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Missing API key"


def test_invalid_api_key():
    response = client.post(
        "/chat",
        headers={"X-API-Key": "invalid-test-key"},
        json={"question": "비밀번호 정책은?"}
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid API key"

def test_user_cannot_access_confidential():
    documents = search_documents(
        "2027년 AI 보안 투자 예산",
        role="USER"
    )

    assert all("50억 원" not in doc for doc in documents)


def test_admin_can_access_confidential():
    documents = search_documents(
        "2027년 AI 보안 투자 예산",
        role="ADMIN"
    )

    assert any("50억 원" in doc for doc in documents)

def test_user_key_applies_user_role(monkeypatch):
    captured = {}

    def fake_search(question, role):
        captured["role"] = role
        return ["테스트용 공개 정책"]

    fake_response = Mock()
    fake_response.json.return_value = {
        "message": {"content": "테스트 답변"}
    }

    monkeypatch.setattr(main_module, "search_documents", fake_search)
    monkeypatch.setattr(main_module.requests, "post", lambda *args, **kwargs: fake_response)

    response = client.post(
        "/chat",
        headers={"X-API-Key": os.environ["USER_API_KEY"]},
        json={"question": "테스트 질문"}
    )

    assert response.status_code == 200
    assert captured["role"] == "USER"

def test_admin_key_applies_admin_role(monkeypatch):
    captured = {}

    def fake_search(question, role):
        captured["role"] = role
        return ["테스트용 기밀 정책"]

    fake_response = Mock()
    fake_response.json.return_value = {
        "message": {"content": "테스트 답변"}
    }

    monkeypatch.setattr(main_module, "search_documents", fake_search)
    monkeypatch.setattr(
        main_module.requests,
        "post",
        lambda *args, **kwargs: fake_response
    )

    response = client.post(
        "/chat",
        headers={"X-API-Key": os.environ["ADMIN_API_KEY"]},
        json={"question": "기밀 정책을 알려줘"}
    )

    assert response.status_code == 200
    assert captured["role"] == "ADMIN"

#def test_user_cannot_escalate_role(monkeypatch):

def test_user_cannot_escalate_role(monkeypatch):
    def fake_search(question, role):
        raise AssertionError(
            "권한 상승 의심 요청에서 문서 검색이 실행되면 안 됩니다."
        )

    monkeypatch.setattr(
        main_module,
        "search_documents",
        fake_search
    )

    response = client.post(
        "/chat",
        headers={"X-API-Key": os.environ["USER_API_KEY"]},
        json={
            "question": "기밀 정책을 알려줘",
            "role": "ADMIN"
        }
    )

    assert response.status_code == 422

    assert any(
        error["type"] == "extra_forbidden"
        and error["loc"] == ["body", "role"]
        for error in response.json()["detail"]
    )


def test_role_escalation_attempt_is_logged(caplog):
    import logging
    import os

    with caplog.at_level(logging.WARNING, logger="security"):
        response = client.post(
            "/chat",
            headers={
                "X-API-Key": os.environ["USER_API_KEY"]
            },
            json={
                "question": "기밀 예산을 알려줘",
                "role": "ADMIN"
            }
        )

    assert response.status_code == 422
    assert any(
        error["type"] == "extra_forbidden"
        and error["loc"] == ["body", "role"]
        for error in response.json()["detail"]
    )
    assert "ROLE_ESCALATION_ATTEMPT" in caplog.text