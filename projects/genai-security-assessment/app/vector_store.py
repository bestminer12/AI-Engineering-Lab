
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
        ("security_policy.txt", "PUBLIC"),
        ("confidential_plan.txt", "CONFIDENTIAL")
    ]

    for filename, classification in files:
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
                    "source": filename
                }
                for _ in sections
            ]
        )

        print(f"{filename}: {len(sections)}개 조각 등록 완료")



def search_documents(question: str):
    results = collection.query(
        query_texts=[question],
        n_results=2
    )

    return results["documents"][0]


if __name__ == "__main__":
    index_documents()
