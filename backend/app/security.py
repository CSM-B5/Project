"""Password hashing (scrypt, standard library) and JWT tokens."""
import hashlib
import hmac
import logging
import os
import secrets
from datetime import datetime, timedelta, timezone
from pathlib import Path

import jwt

from app.config import get_settings

log = logging.getLogger("neuroai.security")

_N, _R, _P = 2**14, 8, 1


def hash_password(password: str) -> str:
    salt = os.urandom(16)
    h = hashlib.scrypt(password.encode(), salt=salt, n=_N, r=_R, p=_P, dklen=64)
    return f"scrypt${_N}${_R}${_P}${salt.hex()}${h.hex()}"


def verify_password(password: str, stored: str) -> bool:
    try:
        _, n, r, p, salt_hex, hash_hex = stored.split("$")
        h = hashlib.scrypt(
            password.encode(), salt=bytes.fromhex(salt_hex), n=int(n), r=int(r), p=int(p), dklen=64
        )
        return hmac.compare_digest(h.hex(), hash_hex)
    except Exception:
        return False


# Used to spend the same time when an email does not exist (prevents user enumeration)
DUMMY_HASH = hash_password("not-a-real-password")

_secret_cache: str | None = None


def get_secret_key() -> str:
    """SECRET_KEY from .env, otherwise a random one saved once to storage/.secret_key."""
    global _secret_cache
    if _secret_cache:
        return _secret_cache
    s = get_settings()
    if s.secret_key:
        _secret_cache = s.secret_key
        return _secret_cache
    path = Path(s.storage_dir) / ".secret_key"
    if path.exists():
        _secret_cache = path.read_text().strip()
    else:
        path.parent.mkdir(parents=True, exist_ok=True)
        _secret_cache = secrets.token_urlsafe(48)
        path.write_text(_secret_cache)
        try:
            path.chmod(0o600)
        except OSError:
            pass
        log.warning("Generated a new secret key at %s", path)
    return _secret_cache


def create_access_token(user_id: int, role: str) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(user_id),
        "role": role,
        "iat": now,
        "exp": now + timedelta(minutes=get_settings().access_token_minutes),
    }
    return jwt.encode(payload, get_secret_key(), algorithm="HS256")


def decode_access_token(token: str) -> dict | None:
    try:
        return jwt.decode(token, get_secret_key(), algorithms=["HS256"])
    except jwt.PyJWTError:
        return None
