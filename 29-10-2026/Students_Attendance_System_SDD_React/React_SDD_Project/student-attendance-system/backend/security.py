
import hashlib
import hmac
import secrets
from datetime import datetime, timedelta, timezone

TOKEN_LIFETIME_HOURS = 8


def hash_password(password: str) -> str:
    salt = secrets.token_bytes(16)
    derived = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode(),
        salt,
        600_000,
    )
    return f"{salt.hex()}${derived.hex()}"


def verify_password(password: str, stored_hash: str) -> bool:
    try:
        salt_hex, expected_hex = stored_hash.split("$", 1)
        actual = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode(),
            bytes.fromhex(salt_hex),
            600_000,
        )
        return hmac.compare_digest(actual.hex(), expected_hex)
    except (ValueError, TypeError):
        return False


def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


def create_token() -> str:
    return secrets.token_urlsafe(32)


def token_expiry():
    return datetime.now(timezone.utc) + timedelta(
        hours=TOKEN_LIFETIME_HOURS
    )
