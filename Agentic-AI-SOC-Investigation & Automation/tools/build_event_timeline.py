
from datetime import datetime, timezone
from opensearchpy import OpenSearch

INDEX_NAME = "soc-security-logs"
MAX_EVENTS = 100

client = OpenSearch(
    hosts=["http://localhost:9200"],
    timeout=30,
)


def parse_time(value: str) -> datetime:
    parsed = datetime.fromisoformat(
        value.replace("Z", "+00:00")
    )

    if parsed.tzinfo is None:
        raise ValueError("Timezone is required")

    return parsed.astimezone(timezone.utc)


def build_event_timeline(
    user_name: str,
    start_time: str,
    end_time: str,
    size: int = 100,
) -> list[dict]:
    """Build a chronological security event timeline."""

    if not isinstance(user_name, str) or not user_name.strip():
        raise ValueError("user_name is required")

    if (
        not isinstance(size, int)
        or isinstance(size, bool)
        or not 1 <= size <= MAX_EVENTS
    ):
        raise ValueError("size must be between 1 and 100")

    start = parse_time(start_time)
    end = parse_time(end_time)

    if start > end:
        raise ValueError("start_time must not exceed end_time")

    query = {
        "size": size,
        "track_total_hits": True,
        "query": {
            "bool": {
                "filter": [
                    {"term": {"user.name": user_name}},
                    {
                        "range": {
                            "@timestamp": {
                                "gte": start.isoformat(),
                                "lte": end.isoformat(),
                            }
                        }
                    },
                ]
            }
        },
        "sort": [
            {"@timestamp": {"order": "asc"}},
            {"event.id": {"order": "asc"}},
        ],
    }

    response = client.search(
        index=INDEX_NAME,
        body=query,
        request_timeout=30,
    )

    total = response["hits"]["total"]
    total_count = (
        total["value"]
        if isinstance(total, dict)
        else total
    )

    if total_count > size:
        raise ValueError(
            "Timeline exceeds the permitted result limit"
        )

    timeline = []

    for hit in response["hits"]["hits"]:
        event = hit["_source"]

        timeline.append({
            "timestamp": event["@timestamp"],
            "event_id": event["event"]["id"],
            "user": event["user"]["name"],
            "action": event["event"]["action"],
            "outcome": event["event"]["outcome"],
            "source_ip": event["source"]["ip"],
        })

    return timeline


if __name__ == "__main__":
    results = build_event_timeline(
        user_name="alice",
        start_time="2026-11-17T00:00:00Z",
        end_time="2026-11-17T01:00:00Z",
    )

    print(f"Timeline contains {len(results)} events")

    for event in results:
        print(
            event["timestamp"],
            event["event_id"],
            event["action"],
            event["outcome"],
            event["source_ip"],
        )
