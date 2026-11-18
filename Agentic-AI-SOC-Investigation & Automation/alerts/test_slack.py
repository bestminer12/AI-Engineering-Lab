
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from alerts.slack_notifier import send_slack_alert


def main():
    # Synthetic test data
    assessment = {
        "user": "alice",
        "severity": "CRITICAL",
        "reasons": [
            "Failed logins followed by successful login",
            "Privilege change observed in investigation timeline",
        ],
        "verified_evidence_count": 9,
        "requires_analyst_review": True,
    }

    send_slack_alert(assessment)


if __name__ == "__main__":
    main()
