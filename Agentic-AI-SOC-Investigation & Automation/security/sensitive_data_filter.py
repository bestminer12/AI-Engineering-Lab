import re

SENSITIVE_KEYS = {
    "password",
    "passwd",
    "secret",
    "api_key",
    "access_token",
    "refresh_token",
    "authorization",
}

SENSITIVE_PATTERNS = [
    re.compile(
        r"(?i)\b(password|passwd|api[_-]?key|access[_-]?token|refresh[_-]?token)\b"
        r"(\s*[:=]\s*)([^\s,;]+)"
    ),
    re.compile(
        r"(?i)\bBearer\s+[A-Za-z0-9._~+/-]+"
    ),
]


def mask_sensitive_data(data):
    """Mask common sensitive fields and credential patterns."""

    if isinstance(data, dict):
        return {
            key: (
                "[REDACTED]"
                if key.lower() in SENSITIVE_KEYS
                else mask_sensitive_data(value)
            )
            for key, value in data.items()
        }

    if isinstance(data, list):
        return [mask_sensitive_data(item) for item in data]

    if isinstance(data, str):
        masked = data

        for pattern in SENSITIVE_PATTERNS:
            if pattern.pattern.startswith("(?i)\\bBearer"):
                masked = pattern.sub("Bearer [REDACTED]", masked)
            else:
                masked = pattern.sub(
                    lambda match: (
                        match.group(1)
                        + match.group(2)
                        + "[REDACTED]"
                    ),
                    masked,
                )

        return masked

    return data