from app.vector_store import collection, search_documents


def test_malicious_document_is_untrusted():
    result = collection.get(
        where={"source": "malicious_notice.txt"},
        include=["metadatas"]
    )

    assert len(result["ids"]) > 0

    assert all(
        metadata["trusted"] is False
        for metadata in result["metadatas"]
    )


def test_user_cannot_retrieve_poisoned_policy():
    documents = search_documents(
        "ABC Corporation의 공식 비밀번호 정책은 최소 몇 자리인가요?",
        role="USER"
    )

    assert all(
        "최소 4자리" not in document
        for document in documents
    )


def test_admin_cannot_retrieve_poisoned_policy():
    documents = search_documents(
        "ABC Corporation의 공식 비밀번호 정책은 최소 몇 자리인가요?",
        role="ADMIN"
    )

    assert all(
        "최소 4자리" not in document
        for document in documents
    )


def test_user_can_retrieve_official_policy():
    documents = search_documents(
        "ABC Corporation의 공식 비밀번호 정책은 최소 몇 자리인가요?",
        role="USER"
    )

    assert any(
        "12자리" in document
        for document in documents
    )