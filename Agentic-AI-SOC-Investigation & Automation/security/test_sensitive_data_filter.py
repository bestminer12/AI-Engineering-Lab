from sensitive_data_filter import mask_sensitive_data

test_data = {
    "user": "alice",
    "password": "test-password-123",
    "api_key": "test-api-key-456",
    "message": "Authorization: Bearer example-token-789",
    "events": [
        {
            "event_id": "AUTH-FAIL-001",
            "access_token": "test-access-token",
            "outcome": "failure",
        }
    ],
}

result = mask_sensitive_data(test_data)

print("=== Masked Result ===")
print(result)

assert result["password"] == "[REDACTED]"
assert result["api_key"] == "[REDACTED]"
assert result["events"][0]["access_token"] == "[REDACTED]"
assert "example-token-789" not in result["message"]
assert result["user"] == "alice"
assert result["events"][0]["outcome"] == "failure"

print("[PASS] Sensitive data masked successfully")