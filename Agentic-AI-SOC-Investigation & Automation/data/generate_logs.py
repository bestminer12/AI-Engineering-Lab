
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

OUTPUT = Path(__file__).parent / "security_logs.jsonl"
BASE_TIME = datetime(2026, 11, 17, 0, 0, tzinfo=timezone.utc)

events = []


def add_event(minutes, event_id, user, ip, action, outcome):
    timestamp = BASE_TIME + timedelta(minutes=minutes)

    events.append({
        "@timestamp": timestamp.isoformat().replace("+00:00", "Z"),
        "event": {
            "id": event_id,
            "category": ["authentication"] if action == "login" else ["iam"],
            "action": action,
            "outcome": outcome,
        },
        "user": {"name": user},
        "source": {"ip": ip},
        "host": {"name": "lab-auth-server"},
    })


# Scenario 1: Repeated authentication failures
for i in range(8):
    add_event(i, f"AUTH-FAIL-{i+1:03}", "alice",
              "198.51.100.10", "login", "failure")

# Scenario 2: Authentication success after failures
add_event(9, "AUTH-SUCCESS-001", "alice",
          "198.51.100.10", "login", "success")

# Scenario 3: Authentication activity from multiple IPs
for i, ip in enumerate([
    "203.0.113.11",
    "203.0.113.12",
    "203.0.113.13",
]):
    add_event(15 + i, f"MULTI-IP-{i+1:03}",
              "bob", ip, "login", "failure")

# Scenario 4: Privilege escalation
add_event(20, "PRIV-ESC-001", "alice",
          "198.51.100.10", "privilege_change", "success")

# Normal events for comparison
for i in range(10):
    add_event(30 + i, f"NORMAL-{i+1:03}",
              f"user{i+1}", "192.0.2.20",
              "login", "success")

with OUTPUT.open("w", encoding="utf-8") as file:
    for event in events:
        file.write(json.dumps(event, ensure_ascii=False) + "\n")

print(f"Generated {len(events)} events: {OUTPUT}")
