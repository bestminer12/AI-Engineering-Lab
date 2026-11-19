
import json
import time
import requests

OPENSEARCH_URL = "http://localhost:9200"
INDEX_NAME = "soc-security-logs"
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "qwen2.5:1.5b"

# Phase 6에서 사용한 동일한 조사 범위
START_TIME = "2026-11-17T00:00:00Z"
END_TIME = "2026-11-17T01:00:00Z"


def fetch_logs():
    query = {
    "size": 100,
    "query": {
        "range": {
            "@timestamp": {
                "gte": START_TIME,
                "lte": END_TIME,
            }
        }
    },
    "sort": [{"@timestamp": {"order": "asc"}}],
    }

    response = requests.post(
        f"{OPENSEARCH_URL}/{INDEX_NAME}/_search",
        json=query,
        timeout=30,
    )
    response.raise_for_status()

    hits = response.json()["hits"]["hits"]

    logs = [hit["_source"] for hit in hits]

    return [
        log for log in logs
        if log.get("user", {}).get("name") == "alice"
    ]


def compact_logs(logs):
    # LLM에 필요한 분석 필드만 전달
    result = []

    for log in logs:
        event = log.get("event", {})
        user = log.get("user", {})
        source = log.get("source", {})

        result.append({
            "timestamp": log.get("@timestamp"),
            "user": user.get("name"),
            "action": event.get("action"),
            "outcome": event.get("outcome"),
            "source_ip": source.get("ip"),
        })

    return result


def main():
    start = time.perf_counter()

    logs = fetch_logs()
    print(f"[INFO] Retrieved logs: {len(logs)}")

    if not logs:
        print("[ERROR] No logs found. Check index and user field.")
        return

    compact = compact_logs(logs)

    prompt = f"""
You are a SOC security analyst.

Analyze the following security logs for user alice.

Answer these questions:
1. How many failed login events occurred?
2. How many successful login events occurred?
3. Was there a privilege change?
4. Was there a failed-login-to-success pattern?
5. What is the risk severity (LOW, MEDIUM, HIGH, CRITICAL)?

Use only the supplied logs.
Do not invent events or timestamps.

Logs:
{json.dumps(compact, ensure_ascii=False)}
"""

    print("[INFO] Ollama analysis started")

    response = requests.post(
        OLLAMA_URL,
        json={
            "model": MODEL_NAME,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": 0, "num_predict": 300},
        },
        timeout=300,
    )
    response.raise_for_status()

    result = response.json()
    elapsed = time.perf_counter() - start

    print("\n=== Single LLM Answer ===")
    print(result.get("response", ""))

    print("\n=== Benchmark Results ===")
    print(f"Total elapsed: {elapsed:.2f}s")
    print(f"Prompt tokens: {result.get('prompt_eval_count', 'N/A')}")
    print(f"Generated tokens: {result.get('eval_count', 'N/A')}")


if __name__ == "__main__":
    main()
