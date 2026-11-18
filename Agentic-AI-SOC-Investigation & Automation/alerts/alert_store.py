
import hashlib
import json
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / "alert_history.db"


def get_connection():
    return sqlite3.connect(DB_PATH, timeout=10)


def init_db():
    """Initialize the alert history database."""

    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS alert_history (
                incident_id TEXT PRIMARY KEY,
                user_name TEXT NOT NULL,
                severity TEXT NOT NULL,
                status TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                sent_at TEXT
            )
        """)


def generate_incident_id(report: dict) -> str:
    """Generate a stable ID for the investigated incident."""

    investigation = report["investigation"]

    evidence_ids = sorted({
        event_id
        for finding in report.get("findings", [])
        for event_id in finding.get("evidence_event_ids", [])
        if isinstance(event_id, str)
    })

    incident_data = {
        "user": investigation["user"],
        "start_time": investigation["start_time"],
        "end_time": investigation["end_time"],
        "evidence_ids": evidence_ids,
    }

    serialized = json.dumps(
        incident_data,
        sort_keys=True,
        ensure_ascii=False,
    )

    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()


def was_alert_sent(incident_id: str) -> bool:
    """Check whether an incident was already sent."""

    with get_connection() as conn:
        row = conn.execute(
            """
            SELECT 1 FROM alert_history
            WHERE incident_id = ? AND status = 'SENT'
            """,
            (incident_id,),
        ).fetchone()

    return row is not None


def record_alert(
    incident_id: str,
    user_name: str,
    severity: str,
    status: str,
):
    """Record the latest alert delivery status."""

    if status not in ("SENT", "FAILED"):
        raise ValueError("Invalid alert status")

    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO alert_history (
                incident_id, user_name, severity, status, sent_at
            )
            VALUES (
                ?, ?, ?, ?,
                CASE WHEN ? = 'SENT'
                     THEN CURRENT_TIMESTAMP
                     ELSE NULL END
            )
            ON CONFLICT(incident_id) DO UPDATE SET
                severity = excluded.severity,
                status = excluded.status,
                sent_at = excluded.sent_at
            WHERE alert_history.status != 'SENT'
            """,
            (
                incident_id,
                user_name,
                severity,
                status,
                status,
            ),
        )


if __name__ == "__main__":
    init_db()
    print("SQLite alert history database initialized")
