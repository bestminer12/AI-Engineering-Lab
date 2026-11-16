
from pathlib import Path
import chromadb
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "chroma_db"
DOCUMENT_PATH = BASE_DIR / "data" / "security_policy.txt"

embedding_function = SentenceTransformerEmbeddingFunction(
    model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
)

client = chromadb.PersistentClient(path=str(DB_PATH))

collection = client.get_or_create_collection(
    name="company_policies_multilingual",
    embedding_function=embedding_function
)





def index_documents():
    files = [
        ("security_policy.txt", "PUBLIC", True),
        ("confidential_plan.txt", "CONFIDENTIAL", True),
        ("malicious_notice.txt", "PUBLIC", False)
    ]

    for filename, classification, trusted in files:
        path = BASE_DIR / "data" / filename
        text = path.read_text(encoding="utf-8")

        sections = [
            section.strip()
            for section in text.split("\n\n")
            if section.strip()
        ]

        collection.upsert(
            

            ids=[
                f"{filename}_{i}"
                for i in range(len(sections))
            ],
            documents=sections,
            metadatas=[
                {
                    "classification": classification,
                    "source": filename,
                    "trusted": trusted
                }
                for _ in sections
            ]
        )

        print(f"{filename}: {len(sections)}개 조각 등록 완료")





def search_documents(
    question: str,
    role: str = "USER",
    max_distance: float | None = None
):
    # 1. 사용자 권한별 문서 접근통제
    if role == "USER":
        where_filter = {
            "$and": [
                {"classification": {"$eq": "PUBLIC"}},
                {"trusted": {"$eq": True}}
            ]
        }

    elif role == "ADMIN":
        where_filter = {"trusted": {"$eq": True}}

    else:
        raise ValueError("Invalid role")

    # 2. ChromaDB 검색
    results = collection.query(
        query_texts=[question],
        n_results=5,
        where=where_filter,
        include=["documents", "distances"]
    )

    documents = results["documents"][0]
    distances = results["distances"][0]

    # 3. 관련성 점수 기반 필터링
    filtered_documents = []

    for document, distance in zip(documents, distances):
        if max_distance is None or distance <= max_distance:
            filtered_documents.append(document)

    return filtered_documents



if __name__ == "__main__":
    index_documents()
