import time
from collections import defaultdict, deque

from app.security_logger import logger


WINDOW_SECONDS = 60
FAILURE_THRESHOLD = 5

# IP별 인증 실패 시각 저장
failed_attempts = defaultdict(deque)


def record_auth_failure(client_ip: str):
    now = time.monotonic()

    attempts = failed_attempts[client_ip]

    # 60초 이전 기록 제거
    while attempts and now - attempts[0] >= WINDOW_SECONDS:
        attempts.popleft()

    # 현재 실패 기록
    attempts.append(now)

    failure_count = len(attempts)

    # 임계치에 도달하면 탐지
    if failure_count == FAILURE_THRESHOLD:
        logger.warning(
            "BRUTE_FORCE_SUSPECTED "
            f"failure_count={failure_count} "
            f"window_seconds={WINDOW_SECONDS}"
        )

    return failure_count
