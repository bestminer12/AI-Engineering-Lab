
import json
from pathlib import Path

from opensearchpy import OpenSearch, helpers

OPENSEARCH_URL = "http://localhost:9200"
INDEX_NAME = "soc-security-logs"
DATA_FILE = Path(__file__).parent / "security_logs.jsonl"

client = OpenSearch(
    hosts=[OPENSEARCH_URL],
    timeout=30,
)

index_body = {
    "settings": {
        "number_of_shards": 1,
        "number_of_replicas": 0,
    },
    "mappings": {
        "properties": {
            "@timestamp": {"type": "date"},
            "event": {
                "properties": {
                    "id": {"type": "keyword"},
                    "category": {"type": "keyword"},
                    "action": {"type": "keyword"},
                    "outcome": {"type": "keyword"},
                }
            },
            "user": {
                "properties": {
                    "name": {"type": "keyword"}
                }
            },
            "source": {
                "properties": {
                    "ip": {"type": "ip"}
                }
            },
            "host": {
                "properties": {
                    "name": {"type": "keyword"}
                }
            },
        }
    },
}


def main():
    if not DATA_FILE.exists():
        raise FileNotFoundError(f"Log file not found: {DATA_FILE}")

    if not client.ping():
        raise ConnectionError("Cannot connect to OpenSearch")

    if not client.indices.exists(index=INDEX_NAME):
        client.indices.create(index=INDEX_NAME, body=index_body)
        print(f"Created index: {INDEX_NAME}")

    actions = []

    with DATA_FILE.open("r", encoding="utf-8") as file:
        for line in file:
            if not line.strip():
                continue

            event = json.loads(line)

            actions.append({
                "_index": INDEX_NAME,
                "_id": event["event"]["id"],
                "_source": event,
            })

    success, errors = helpers.bulk(
        client,
        actions,
        raise_on_error=False,
        refresh="wait_for",
    )

    print(f"Indexed documents: {success}")

    if errors:
        print(f"Indexing errors: {len(errors)}")
        raise RuntimeError("Some documents failed to index")

    count = client.count(index=INDEX_NAME)["count"]
    print(f"Total documents in index: {count}")


if __name__ == "__main__":
    main()
