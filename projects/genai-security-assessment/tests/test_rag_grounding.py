
from app import vector_store


def test_relevant_document_is_allowed(monkeypatch):
    """거리 0.25인 문서는 허용한다."""

    def fake_query(**kwargs):
        return {
            "documents": [["정상 보안 정책"]],
            "distances": [[0.25]]
        }

    monkeypatch.setattr(
        vector_store.collection,
        "query",
        fake_query
    )

    documents = vector_store.search_documents(
        "회사 비밀번호 정책",
        role="USER",
        max_distance=0.5
    )

    assert documents == ["정상 보안 정책"]


def test_irrelevant_document_is_blocked(monkeypatch):
    """거리 0.85인 문서는 제외한다."""

    def fake_query(**kwargs):
        return {
            "documents": [["관련 없는 문서"]],
            "distances": [[0.85]]
        }

    monkeypatch.setattr(
        vector_store.collection,
        "query",
        fake_query
    )

    documents = vector_store.search_documents(
        "대한민국 수도",
        role="USER",
        max_distance=0.5
    )

    assert documents == []


def test_no_documents_prevents_llm_call(monkeypatch):
    """관련 문서가 없으면 LLM을 호출하지 않아야 한다."""

    from fastapi.testclient import TestClient
    from app import main

    # 인증 의존성은 테스트용 USER로 대체
    main.app.dependency_overrides[main.get_current_user] = (
        lambda: {"username": "user", "role": "USER"}
    )

    # 검색 결과가 없는 상황 재현
    monkeypatch.setattr(
        main,
        "search_documents",
        lambda question, role, max_distance: []
    )

    # LLM이 호출되면 테스트 실패
    def fail_if_llm_called(*args, **kwargs):
        raise AssertionError("LLM should not be called")

    monkeypatch.setattr(
        main.requests,
        "post",
        fail_if_llm_called
    )

    try:
        client = TestClient(main.app)

        response = client.post(
            "/chat",
            json={"question": "대한민국의 수도는 어디인가요?"}
        )

        assert response.status_code == 200
        assert response.json() == {
            "answer": "회사 정책 문서에서 관련 정보를 찾을 수 없습니다."
        }

    finally:
        # 다른 테스트에 영향을 주지 않도록 인증 설정 복원
        main.app.dependency_overrides.pop(
            main.get_current_user,
            None
        )
