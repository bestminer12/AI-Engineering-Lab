from typing import Any


def calculate_severity(report: dict[str, Any]) -> dict:
    """Determine severity using verified investigation evidence."""

    if not isinstance(report, dict):
        raise ValueError("report must be a dictionary")

    if report.get("report_type") != "security_investigation":
        raise ValueError("Invalid investigation report")

    if report.get("assessment_status") != "requires_analyst_review":
        raise ValueError("Unexpected assessment status")

    investigation = report.get("investigation", {})
    user_name = investigation.get("user")

    if not isinstance(user_name, str) or not user_name.strip():
        raise ValueError("Investigation user is required")

    summary = report.get("summary", {})
    verified_count = summary.get("verified_evidence_count", 0)

    if not isinstance(verified_count, int) or isinstance(verified_count, bool):
        raise ValueError("Invalid verified evidence count")

    if verified_count < 0:
        raise ValueError("Invalid verified evidence count")

    findings = report.get("findings", [])
    timeline = report.get("timeline", [])

    if not isinstance(findings, list) or not isinstance(timeline, list):
        raise ValueError("Invalid report findings or timeline")

    # Only consider events present in the verified timeline.
    has_login_success = any(
        event.get("action") == "login"
        and event.get("outcome") == "success"
        for event in timeline
    )

    has_privilege_change = any(
        event.get("action") == "privilege_change"
        and event.get("outcome") == "success"
        for event in timeline
    )

    failure_to_success = any(
        finding.get("pattern") == "failure_to_success"
        for finding in findings
    )

    multi_source_ips = any(
        finding.get("pattern") == "multiple_source_ips"
        for finding in findings
    )

    reasons = []

    if verified_count == 0:
        severity = "LOW"
        reasons.append("No verified evidence found")

    elif failure_to_success and has_login_success and has_privilege_change:
        severity = "CRITICAL"
        reasons.append("Failed logins followed by successful login")
        reasons.append("Privilege change observed in investigation timeline")

    elif failure_to_success and has_login_success:
        severity = "HIGH"
        reasons.append("Failed logins followed by successful login")

    elif multi_source_ips or verified_count >= 5:
        severity = "MEDIUM"
        reasons.append("Suspicious authentication activity detected")

    else:
        severity = "LOW"
        reasons.append("Limited suspicious activity")

    return {
        "user": user_name,
        "severity": severity,
        "reasons": reasons,
        "verified_evidence_count": verified_count,
        "requires_analyst_review": True,
    }


if __name__ == "__main__":
    print("Severity engine module ready")
