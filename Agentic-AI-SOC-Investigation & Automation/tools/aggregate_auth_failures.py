
from datetime import datetime, timezone
from opensearchpy import OpenSearch

INDEX_NAME = "soc-security-logs"

client = OpenSearch(
    hosts=["http://localhost:9200"],
    timeout=30,
)


def aggregate_auth_failures(
    start_time: str,
    end_time: str,
    min_failures: int = 3,
) -> list[dict]:
    """Aggregate failed login events by user and source IP."""

    def parse_time(value: str) -> datetime:
        parsed = datetime.fromisoformat(
            value.replace("Z", "+00:00")
        )
        if parsed.tzinfo is None:
            raise ValueError("Timezone is required")
        return parsed.astimezone(timezone.utc)

    start = parse_time(start_time)
    end = parse_time(end_time)

    if start > end:
        raise ValueError("start_time must not exceed end_time")

    if not isinstance(min_failures, int) or isinstance(min_failures, bool):
        raise ValueError("min_failures must be an integer")

    if not 1 <= min_failures <= 100:
        raise ValueError("min_failures must be between 1 and 100")

    query = {
        "size": 0,
        "query": {
            "bool": {
                "filter": [
                    {"term": {"event.action": "login"}},
                    {"term": {"event.outcome": "failure"}},
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
        "aggs": {
            "by_user": {
                "terms": {
                    "field": "user.name",
                    "size": 100,
                },
                "aggs": {
                    "by_ip": {
                        "terms": {
                            "field": "source.ip",
                            "size": 100,
                        },
                        "aggs": {
                            "first_seen": {
                                "min": {"field": "@timestamp"}
                            },
                            "last_seen": {
                                "max": {"field": "@timestamp"}
                            },
                        },
                    }
                },
            }
        },
    }

    response = client.search(
        index=INDEX_NAME,
        body=query,
        request_timeout=30,
    )

    results = []

    for user_bucket in response["aggregations"]["by_user"]["buckets"]:
        for ip_bucket in user_bucket["by_ip"]["buckets"]:
            count = ip_bucket["doc_count"]

            if count < min_failures:
                continue

            results.append({
                "user": user_bucket["key"],
                "source_ip": ip_bucket["key"],
                "failure_count": count,
                "first_seen": ip_bucket["first_seen"]["value_as_string"],
                "last_seen": ip_bucket["last_seen"]["value_as_string"],
            })

    return sorted(
        results,
        key=lambda item: item["failure_count"],
        reverse=True,
    )


if __name__ == "__main__":
    results = aggregate_auth_failures(
        start_time="2026-11-17T00:00:00Z",
        end_time="2026-11-17T01:00:00Z",
        min_failures=3,
    )

    print(f"Found {len(results)} suspicious groups")

    for result in results:
        print(result)
