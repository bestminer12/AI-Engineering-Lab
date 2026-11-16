import os
import secrets

from fastapi import HTTPException, Security
from fastapi.security import APIKeyHeader

from dotenv import load_dotenv
from app.security_logger import logger

from fastapi import Request
from app.detection import record_auth_failure

load_dotenv()


api_key_header = APIKeyHeader(
    name="X-API-Key",
    auto_error=False
)



def get_current_user(
    request: Request,
    api_key: str | None = Security(api_key_header)
):
    user_key = os.getenv("USER_API_KEY")
    admin_key = os.getenv("ADMIN_API_KEY")

    # 1. 인증 환경변수 설정 오류
    if not user_key or not admin_key or user_key == admin_key:
        logger.error("AUTH_CONFIG_ERROR")

        raise HTTPException(
            status_code=503,
            detail="Authentication is not configured"
        )

    # 클라이언트 IP 확인
    client_ip = (
        request.client.host
        if request.client
        else "unknown"
    )

    # 2. API Key 누락
    if api_key is None:
        logger.warning(
            "AUTH_FAILURE reason=MISSING_API_KEY"
        )

        # 인증 실패 횟수 기록
        record_auth_failure(client_ip)

        raise HTTPException(
            status_code=401,
            detail="Missing API key"
        )

    # 3. ADMIN 인증 성공
    if secrets.compare_digest(api_key, admin_key):
        logger.info("AUTH_SUCCESS role=ADMIN")

        return {
            "username": "admin",
            "role": "ADMIN"
        }

    # 4. USER 인증 성공
    if secrets.compare_digest(api_key, user_key):
        logger.info("AUTH_SUCCESS role=USER")

        return {
            "username": "user",
            "role": "USER"
        }

    # 5. 잘못된 API Key
    logger.warning(
        "AUTH_FAILURE reason=INVALID_API_KEY"
    )

    # 인증 실패 횟수 기록
    record_auth_failure(client_ip)

    raise HTTPException(
        status_code=401,
        detail="Invalid API key"
    )


