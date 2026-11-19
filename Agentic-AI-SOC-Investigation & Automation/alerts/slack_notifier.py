
import os

import requests
from dotenv import load_dotenv

from security.sensitive_data_filter import mask_sensitive_data


load_dotenv()


def send_slack_alert(assessment: dict) -> bool:
    """Send HIGH/CRITICAL security alerts to Slack."""

    severity = assessment.get("severity")

    if severity not in ("HIGH", "CRITICAL"):
        print("[SKIPPED] Severity below HIGH")
        return False

    webhook_url = os.getenv("SLACK_WEBHOOK_URL")

    if not webhook_url:
        raise ValueError("SLACK_WEBHOOK_URL is not configured")

    user = assessment.get("user", "unknown")
    reasons = assessment.get("reasons", [])
    evidence_count = assessment.get("verified_evidence_count", 0)

    # 1. Slack 메시지 생성
    message = {
        "text": (
            f"🚨 SOC Security Alert\n"
            f"Severity: {severity}\n"
            f"User: {user}\n"
            f"Verified Evidence: {evidence_count}\n"
            f"Reasons:\n"
            + "\n".join(f"- {reason}" for reason in reasons)
            + "\nStatus: Requires Analyst Review"
        )
    }

    # 2. Slack 전송 전 민감정보 마스킹
    safe_message = mask_sensitive_data(message)

    # 3. 마스킹된 메시지만 Slack으로 전송
    response = requests.post(
        webhook_url,
        json=safe_message,
        timeout=10,
    )
    response.raise_for_status()

    if response.text.strip() != "ok":
        raise RuntimeError("Unexpected Slack response")

    print("[SUCCESS] Slack alert sent")
    return True
