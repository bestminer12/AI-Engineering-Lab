
from unittest.mock import patch, Mock

from alerts.slack_notifier import send_slack_alert


assessment = {
    "severity": "CRITICAL",
    "user": "alice",
    "verified_evidence_count": 9,
    "reasons": [
        "Failed logins followed by successful login",
        "api_key=TEST-SECRET-12345",
    ],
}

mock_response = Mock()
mock_response.status_code = 200
mock_response.text = "ok"
mock_response.raise_for_status.return_value = None

with patch("alerts.slack_notifier.requests.post", return_value=mock_response) as mock_post:
    result = send_slack_alert(assessment)

    sent_payload = mock_post.call_args.kwargs["json"]

    print("\n=== Slack Payload ===")
    print(sent_payload["text"])

    assert result is True
    assert "TEST-SECRET-12345" not in sent_payload["text"]
    assert "api_key=[REDACTED]" in sent_payload["text"]
    assert "Failed logins followed by successful login" in sent_payload["text"]

    print("[PASS] Sensitive data removed before Slack transmission")
