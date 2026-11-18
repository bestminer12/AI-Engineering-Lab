
import json

from tools.correlate_auth_events import correlate_auth_events
from tools.build_event_timeline import build_event_timeline
from tools.generate_investigation_report import generate_investigation_report

from severity.severity_engine import calculate_severity
from alerts.slack_notifier import send_slack_alert
from alerts.alert_store import (
    init_db,
    generate_incident_id,
    was_alert_sent,
    record_alert,
)


USER_NAME = "alice"
START_TIME = "2026-11-17T00:00:00Z"
END_TIME = "2026-11-17T01:00:00Z"


def main():
    init_db()

    print("\n=== Step 1: Correlation Analysis ===")

    findings = correlate_auth_events(
        start_time=START_TIME,
        end_time=END_TIME,
        failure_threshold=3,
        window_minutes=15,
    )

    print(f"Correlation findings: {len(findings)}")

    print("\n=== Step 2: Event Timeline ===")

    timeline = build_event_timeline(
        user_name=USER_NAME,
        start_time=START_TIME,
        end_time=END_TIME,
        size=100,
    )

    print(f"Timeline events: {len(timeline)}")

    print("\n=== Step 3: Investigation Report ===")

    report = generate_investigation_report(
        user_name=USER_NAME,
        start_time=START_TIME,
        end_time=END_TIME,
        findings=findings,
        timeline=timeline,
    )

    print("Investigation report generated")
    print("Report summary:", report["summary"])

    print("\n=== Step 4: Severity Assessment ===")

    assessment = calculate_severity(report)
    print(json.dumps(assessment, indent=2, ensure_ascii=False))

    print("\n=== Step 5: Incident Identification ===")

    incident_id = generate_incident_id(report)
    print(f"Incident ID: {incident_id[:16]}...")

    print("\n=== Step 6: Slack Notification ===")

    if assessment["severity"] not in ("HIGH", "CRITICAL"):
        print("[SKIPPED] Severity below HIGH")
        return

    if was_alert_sent(incident_id):
        print("[SKIPPED] Duplicate alert already sent")
        return

    try:
        sent = send_slack_alert(assessment)

        if sent:
            record_alert(
                incident_id=incident_id,
                user_name=assessment["user"],
                severity=assessment["severity"],
                status="SENT",
            )
            print("[RECORDED] Alert delivery status: SENT")

    except Exception as exc:
        record_alert(
            incident_id=incident_id,
            user_name=assessment["user"],
            severity=assessment["severity"],
            status="FAILED",
        )
        print(f"[FAILED] Slack delivery: {type(exc).__name__}")
        raise


if __name__ == "__main__":
    main()
