
from app.vector_store import search_documents


def test_user_can_read_public_document():
    documents = search_documents(
        "비밀번호 정책",
        role="USER"
    )

    assert any(
        "12자리" in document
        for document in documents
    )


def test_user_cannot_read_confidential_document():
    documents = search_documents(
        "2027년 AI 보안 사업 투자 예산",
        role="USER"
    )

    assert all(
        "50억 원" not in document
        for document in documents
    )


def test_admin_can_read_confidential_document():
    documents = search_documents(
        "2027년 AI 보안 사업 투자 예산",
        role="ADMIN"
    )

    assert any(
        "50억 원" in document
        for document in documents
    )
