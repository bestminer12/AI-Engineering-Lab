
import json
from datetime import datetime, timezone

from opensearchpy import OpenSearch

INDEX_NAME = "soc-security-logs"
MAX_EVIDENCE = 100

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


def generate_investigation_report(
    user_name: str,
    start_time: str,
    end_time: str,
    findings: list[dict],
    timeline: list[dict],
) -> dict:
    """Generate a report with verified event evidence."""

    if not isinstance(user_name, str) or not user_name.strip():
        raise ValueError("user_name is required")

    start = parse_time(start_time)
    end = parse_time(end_time)

    if start > end:
        raise ValueError("Invalid time range")

    if not isinstance(findings, list):
        raise ValueError("findings must be a list")

    if not isinstance(timeline, list):
        raise ValueError("timeline must be a list")

    # Keep only findings for the investigated user.
    selected_findings = [
        finding
        for finding in findings
        if finding.get("user") == user_name
    ]

    evidence_ids = set()

    for finding in selected_findings:
        for event_id in finding.get("evidence_event_ids", []):
            evidence_ids.add(event_id)

    if len(evidence_ids) > MAX_EVIDENCE:
        raise ValueError("Too many evidence events")

    verified_evidence = []

    if evidence_ids:
        response = client.search(
            index=INDEX_NAME,
            body={
                "size": MAX_EVIDENCE,
                "query": {
                    "bool": {
                        "filter": [
                            {
                                "terms": {
                                    "event.id": sorted(evidence_ids)
                                }
                            },
                            {
                                "term": {
                                    "user.name": user_name
                                }
                            },
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
            },
            request_timeout=30,
        )

        verified_evidence = [
            {
                "event_id": hit["_source"]["event"]["id"],
                "timestamp": hit["_source"]["@timestamp"],
                "action": hit["_source"]["event"]["action"],
                "outcome": hit["_source"]["event"]["outcome"],
            }
            for hit in response["hits"]["hits"]
        ]

    verified_ids = {
        event["event_id"]
        for event in verified_evidence
    }

    if evidence_ids != verified_ids:
        missing = evidence_ids - verified_ids
        raise ValueError(
            f"Unverified evidence IDs: {sorted(missing)}"
        )

    # Verify timeline events against the same evidence source.
    timeline_ids = {
        event["event_id"]
        for event in timeline
    }

    if len(timeline_ids) != len(timeline):
        raise ValueError("Duplicate timeline event IDs")

    if len(timeline_ids) > MAX_EVIDENCE:
        raise ValueError("Too many timeline events")

    if timeline_ids:
        response = client.search(
            index=INDEX_NAME,
            body={
                "size": MAX_EVIDENCE,
                "query": {
                    "bool": {
                        "filter": [
                            {"terms": {"event.id": sorted(timeline_ids)}},
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
            },
            request_timeout=30,
        )

        actual_timeline = {
            hit["_source"]["event"]["id"]: hit["_source"]
            for hit in response["hits"]["hits"]
        }

        if set(actual_timeline) != timeline_ids:
            raise ValueError("Timeline contains unverified events")

        for event in timeline:
            actual = actual_timeline[event["event_id"]]
            if (
                event.get("timestamp") != actual["@timestamp"]
                or event.get("action") != actual["event"]["action"]
                or event.get("outcome") != actual["event"]["outcome"]
                or event.get("source_ip") != actual["source"]["ip"]
                or event.get("user") != actual["user"]["name"]
            ):
                raise ValueError(
                    f"Timeline data mismatch: {event['event_id']}"
                )

    report = {
        "report_type": "security_investigation",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "investigation": {
            "user": user_name,
            "start_time": start.isoformat(),
            "end_time": end.isoformat(),
        },
        "summary": {
            "finding_count": len(selected_findings),
            "timeline_event_count": len(timeline),
            "verified_evidence_count": len(verified_evidence),
        },
        "findings": selected_findings,
        "verified_evidence": sorted(
            verified_evidence,
            key=lambda item: item["timestamp"],
        ),
        "timeline": sorted(
            timeline,
            key=lambda item: item["timestamp"],
        ),
        "assessment_status": "requires_analyst_review",
    }

    return report


if __name__ == "__main__":
    from correlate_auth_events import correlate_auth_events
    from build_event_timeline import build_event_timeline

    START = "2026-11-17T00:00:00Z"
    END = "2026-11-17T01:00:00Z"
    USER = "alice"

    findings = correlate_auth_events(
        start_time=START,
        end_time=END,
    )

    timeline = build_event_timeline(
        user_name=USER,
        start_time=START,
        end_time=END,
    )

    report = generate_investigation_report(
        user_name=USER,
        start_time=START,
        end_time=END,
        findings=findings,
        timeline=timeline,
    )

    print(json.dumps(report, indent=2, ensure_ascii=False))
