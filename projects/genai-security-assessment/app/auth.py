import os
import secrets

from fastapi import HTTPException, Security
from fastapi.security import APIKeyHeader

from dotenv import load_dotenv

load_dotenv()


api_key_header = APIKeyHeader(
    name="X-API-Key",
    auto_error=False
)


def get_current_user(
    api_key: str | None = Security(api_key_header)
):
    user_key = os.getenv("USER_API_KEY")
    admin_key = os.getenv("ADMIN_API_KEY")

    if not user_key or not admin_key or user_key == admin_key:
        raise HTTPException(
            status_code=503,
            detail="Authentication is not configured"
        )

    if api_key is None:
        raise HTTPException(
            status_code=401,
            detail="Missing API key"
        )

    if secrets.compare_digest(api_key, admin_key):
        return {"username": "admin", "role": "ADMIN"}

    if secrets.compare_digest(api_key, user_key):
        return {"username": "user", "role": "USER"}

    raise HTTPException(
        status_code=401,
        detail="Invalid API key"
    )