
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from opensearchpy import OpenSearch

INDEX_NAME = "soc-security-logs"
MAX_EVENTS = 1000

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


def correlate_auth_events(
    start_time: str,
    end_time: str,
    failure_threshold: int = 3,
    window_minutes: int = 15,
) -> list[dict]:
    """Identify failure-to-success and multi-IP patterns."""

    start = parse_time(start_time)
    end = parse_time(end_time)

    if start > end:
        raise ValueError("start_time must not exceed end_time")

    if (
        not isinstance(failure_threshold, int)
        or isinstance(failure_threshold, bool)
        or not 1 <= failure_threshold <= 100
    ):
        raise ValueError("Invalid failure_threshold")

    if (
        not isinstance(window_minutes, int)
        or isinstance(window_minutes, bool)
        or not 1 <= window_minutes <= 1440
    ):
        raise ValueError("Invalid window_minutes")

    query = {
        "size": MAX_EVENTS,
        "query": {
            "bool": {
                "filter": [
                    {"term": {"event.action": "login"}},
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

    hits = response["hits"]["hits"]

    total = response["hits"]["total"]
    total_count = (
        total["value"] if isinstance(total, dict)
        else total
    )

    if total_count > MAX_EVENTS:
        raise ValueError(
            "Too many events for bounded correlation"
        )

    events_by_user = defaultdict(list)

    for hit in hits:
        event = hit["_source"]
        events_by_user[event["user"]["name"]].append(event)

    findings = []
    window = timedelta(minutes=window_minutes)

    for user_name, events in events_by_user.items():

        # Pattern 1: Failed logins followed by success
        for event in events:
            if event["event"]["outcome"] != "success":
                continue

            success_time = parse_time(event["@timestamp"])
            success_ip = event["source"]["ip"]

            failures = [
                previous
                for previous in events
                if (
                    previous["event"]["outcome"] == "failure"
                    and previous["source"]["ip"] == success_ip
                    and success_time - window
                    <= parse_time(previous["@timestamp"])
                    < success_time
                )
            ]

            if len(failures) >= failure_threshold:
                findings.append({
                    "pattern": "failure_to_success",
                    "user": user_name,
                    "source_ip": success_ip,
                    "failure_count": len(failures),
                    "success_event_id": event["event"]["id"],
                    "evidence_event_ids": [
                        item["event"]["id"]
                        for item in failures
                    ] + [event["event"]["id"]],
                })

        # Pattern 2: Multiple source IPs for one user
        ip_to_events = defaultdict(list)

        for event in events:
            ip_to_events[event["source"]["ip"]].append(event)

        if len(ip_to_events) >= 3:
            findings.append({
                "pattern": "multiple_source_ips",
                "user": user_name,
                "source_ip_count": len(ip_to_events),
                "source_ips": sorted(ip_to_events.keys()),
                "evidence_event_ids": [
                    event["event"]["id"]
                    for event in events
                ],
            })

    return findings


if __name__ == "__main__":
    results = correlate_auth_events(
        start_time="2026-11-17T00:00:00Z",
        end_time="2026-11-17T01:00:00Z",
        failure_threshold=3,
        window_minutes=15,
    )

    print(f"Found {len(results)} correlation findings")

    for result in results:
        print(result)
