
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from tools.correlate_auth_events import correlate_auth_events
from tools.build_event_timeline import build_event_timeline
from tools.generate_investigation_report import generate_investigation_report
from severity.severity_engine import calculate_severity


USER_NAME = "alice"
START_TIME = "2026-11-17T00:00:00Z"
END_TIME = "2026-11-17T01:00:00Z"


def main():
    # Step 1: Collect investigation findings
    findings = correlate_auth_events(
        start_time=START_TIME,
        end_time=END_TIME,
        failure_threshold=3,
        window_minutes=15,
    )

    # Step 2: Build event timeline
    timeline = build_event_timeline(
        user_name=USER_NAME,
        start_time=START_TIME,
        end_time=END_TIME,
        size=100,
    )

    # Step 3: Generate verified investigation report
    report = generate_investigation_report(
        user_name=USER_NAME,
        start_time=START_TIME,
        end_time=END_TIME,
        findings=findings,
        timeline=timeline,
    )

    # Step 4: Calculate severity
    result = calculate_severity(report)

    print("\n=== Severity Assessment ===")
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
