
import json
import logging
from pathlib import Path

from app.security_logger import JSONFormatter


def test_security_log_json_format():
    """보안 이벤트가 올바른 JSON 형식으로 변환되는지 확인"""

    formatter = JSONFormatter()

    record = logging.LogRecord(
        name="security",
        level=logging.WARNING,
        pathname=__file__,
        lineno=1,
        msg="AUTH_FAILURE reason=INVALID_API_KEY",
        args=(),
        exc_info=None
    )

    result = json.loads(formatter.format(record))

    assert result["level"] == "WARNING"
    assert result["event_type"] == "AUTH_FAILURE"
    assert result["reason"] == "INVALID_API_KEY"
    assert "timestamp" in result


def test_security_log_file_handler():
    """로그 파일 저장 핸들러가 설정되어 있는지 확인"""

    from logging.handlers import RotatingFileHandler
    from app.security_logger import logger

    file_handlers = [
        handler
        for handler in logger.handlers
        if isinstance(handler, RotatingFileHandler)
    ]

    assert len(file_handlers) == 1

    handler = file_handlers[0]

    assert Path(handler.baseFilename).name == "security.jsonl"
    assert handler.maxBytes == 5 * 1024 * 1024
    assert handler.backupCount == 3



def test_security_log_rotation(tmp_path):
    """로그 파일 크기 초과 시 백업 파일이 생성되는지 확인"""

    from logging.handlers import RotatingFileHandler

    log_file = tmp_path / "security.jsonl"

    handler = RotatingFileHandler(
        filename=log_file,
        maxBytes=200,
        backupCount=2,
        encoding="utf-8"
    )

    handler.setFormatter(JSONFormatter())

    test_logger = logging.getLogger("security.rotation.test")
    test_logger.setLevel(logging.INFO)
    test_logger.addHandler(handler)

    try:
        for _ in range(10):
            test_logger.info(
                "AUTH_FAILURE reason=INVALID_API_KEY"
            )

        handler.flush()

        assert log_file.exists()
        assert (tmp_path / "security.jsonl.1").exists()

    finally:
        test_logger.removeHandler(handler)
        handler.close()
