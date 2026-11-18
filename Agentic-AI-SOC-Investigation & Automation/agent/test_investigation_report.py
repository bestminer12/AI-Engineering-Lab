
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from tools.correlate_auth_events import correlate_auth_events
from tools.build_event_timeline import build_event_timeline
from tools.generate_investigation_report import (
    generate_investigation_report,
)

USER_NAME = "alice"
START_TIME = "2026-11-17T00:00:00Z"
END_TIME = "2026-11-17T01:00:00Z"


def main():
    print("=== Step 1: Correlation Analysis ===")

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

    print("\n=== Step 3: Generate Investigation Report ===")

    report = generate_investigation_report(
        user_name=USER_NAME,
        start_time=START_TIME,
        end_time=END_TIME,
        findings=findings,
        timeline=timeline,
    )

    print(json.dumps(report, indent=2, ensure_ascii=False))

    print("\n=== Report Verification ===")

    print("Report type:", report.get("report_type"))
    print("Investigation user:", report.get("investigation", {}).get("user"))
    print("Summary:", report.get("summary"))


if __name__ == "__main__":
    main()
