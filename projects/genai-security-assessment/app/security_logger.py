
import json
import logging
from datetime import datetime, timezone
from logging.handlers import RotatingFileHandler
from pathlib import Path


class JSONFormatter(logging.Formatter):
    def format(self, record):
        parts = record.getMessage().split()
        event_type = parts[0] if parts else "UNKNOWN"

        event_data = {}

        for part in parts[1:]:
            if "=" in part:
                key, value = part.split("=", 1)
                event_data[key] = value

        log_data = {
            "timestamp": datetime.fromtimestamp(
                record.created, timezone.utc
            ).astimezone().isoformat(),
            "level": record.levelname,
            "event_type": event_type,
            **event_data
        }

        return json.dumps(log_data, ensure_ascii=False)


logger = logging.getLogger("security")
logger.setLevel(logging.INFO)

if not logger.handlers:
    formatter = JSONFormatter()

    # 1. 콘솔 로그 출력
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # 2. 로그 저장 디렉터리 생성
    project_root = Path(__file__).resolve().parent.parent
    log_dir = project_root / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)

    # 3. JSON 로그 파일 저장 및 로테이션
    file_handler = RotatingFileHandler(
        filename=log_dir / "security.jsonl",
        maxBytes=5 * 1024 * 1024,
        backupCount=3,
        encoding="utf-8"
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

logger.propagate = False
