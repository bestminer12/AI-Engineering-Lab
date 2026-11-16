
import logging

import pytest

from app import detection


@pytest.fixture(autouse=True)
def reset_detection_state():
    # 테스트 간 인증 실패 기록이 섞이지 않도록 초기화
    detection.failed_attempts.clear()
    yield
    detection.failed_attempts.clear()


def test_four_failures_do_not_trigger_alert(caplog):
    """인증 실패 4회까지는 경고가 발생하지 않아야 한다."""

    with caplog.at_level(logging.WARNING, logger="security"):
        for _ in range(4):
            count = detection.record_auth_failure("192.0.2.10")

    assert count == 4
    assert "BRUTE_FORCE_SUSPECTED" not in caplog.text


def test_five_failures_trigger_alert(caplog):
    """인증 실패 5회째에 탐지 경고가 발생해야 한다."""

    with caplog.at_level(logging.WARNING, logger="security"):
        for _ in range(5):
            count = detection.record_auth_failure("192.0.2.10")

    assert count == 5
    assert "BRUTE_FORCE_SUSPECTED" in caplog.text


def test_different_ips_are_counted_separately():
    """IP별 인증 실패 횟수가 독립적으로 집계되어야 한다."""

    for _ in range(4):
        detection.record_auth_failure("192.0.2.10")

    count = detection.record_auth_failure("192.0.2.20")

    assert count == 1
    assert len(detection.failed_attempts["192.0.2.10"]) == 4
    assert len(detection.failed_attempts["192.0.2.20"]) == 1


def test_failures_expire_after_60_seconds(monkeypatch):
    """60초가 지난 인증 실패 기록은 집계에서 제외한다."""

    current_time = 1000.0

    # 탐지 모듈에서 사용하는 시간을 테스트용으로 고정
    monkeypatch.setattr(
        detection.time,
        "monotonic",
        lambda: current_time
    )

    # 최초 인증 실패 4회
    for _ in range(4):
        count = detection.record_auth_failure("192.0.2.10")

    assert count == 4

    # 61초 경과
    current_time += 61

    # 이전 4회는 만료되었으므로 새로운 실패는 1회
    count = detection.record_auth_failure("192.0.2.10")

    assert count == 1
