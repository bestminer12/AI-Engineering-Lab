
from datetime import datetime, timezone
from opensearchpy import OpenSearch

INDEX_NAME = "soc-security-logs"
MAX_RESULTS = 100

client = OpenSearch(
    hosts=["http://localhost:9200"],
    timeout=30,
)


def search_security_logs(
    user_name: str | None = None,
    source_ip: str | None = None,
    outcome: str | None = None,
    start_time: str | None = None,
    end_time: str | None = None,
    size: int = 20,
) -> list[dict]:
    """Search security logs using approved filters."""

    if not isinstance(size, int) or isinstance(size, bool):
        raise ValueError("size must be an integer")

    if not 1 <= size <= MAX_RESULTS:
        raise ValueError("size must be between 1 and 100")

    if outcome not in (None, "success", "failure"):
        raise ValueError("Invalid outcome")

    def parse_time(value):
        if value is None:
            return None
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        if parsed.tzinfo is None:
            raise ValueError("Timezone is required")
        return parsed.astimezone(timezone.utc)

    start = parse_time(start_time)
    end = parse_time(end_time)

    if start and end and start > end:
        raise ValueError("start_time must not exceed end_time")

    filters = []

    if user_name:
        filters.append({"term": {"user.name": user_name}})

    if source_ip:
        filters.append({"term": {"source.ip": source_ip}})

    if outcome:
        filters.append({"term": {"event.outcome": outcome}})

    time_range = {}
    if start:
        time_range["gte"] = start.isoformat()
    if end:
        time_range["lte"] = end.isoformat()

    if time_range:
        filters.append({"range": {"@timestamp": time_range}})

    query = {
        "size": size,
        "query": {
            "bool": {
                "filter": filters
            }
        },
        "sort": [
            {"@timestamp": {"order": "asc"}}
        ],
    }

    response = client.search(
        index=INDEX_NAME,
        body=query,
        request_timeout=30,
    )

    return [
        hit["_source"]
        for hit in response["hits"]["hits"]
    ]


if __name__ == "__main__":
    results = search_security_logs(
        user_name="alice",
        outcome="failure",
    )

    print(f"Found {len(results)} events")

    for event in results:
        print(
            event["@timestamp"],
            event["event"]["id"],
            event["user"]["name"],
            event["source"]["ip"],
            event["event"]["outcome"],
        )
