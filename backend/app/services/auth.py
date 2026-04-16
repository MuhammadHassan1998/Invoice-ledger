import base64
import hashlib
import hmac
import json
import os
import secrets
import time
from typing import Any

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.database import get_app_db
from app.models.user import User

_HASH_ALGORITHM = "sha256"
_HASH_ITERATIONS = 210_000
_TOKEN_TTL_SECONDS = int(os.getenv("AUTH_TOKEN_TTL_SECONDS", "86400"))
_AUTH_SECRET = os.getenv("AUTH_SECRET", "dev-invoice-ledger-secret").encode("utf-8")

bearer_scheme = HTTPBearer(auto_error=False)


def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac(
        _HASH_ALGORITHM,
        password.encode("utf-8"),
        salt.encode("utf-8"),
        _HASH_ITERATIONS,
    ).hex()
    return f"pbkdf2_{_HASH_ALGORITHM}${_HASH_ITERATIONS}${salt}${digest}"


def verify_password(password: str, password_hash: str) -> bool:
    try:
        algorithm, iterations, salt, expected = password_hash.split("$", 3)
        hash_name = algorithm.removeprefix("pbkdf2_")
        digest = hashlib.pbkdf2_hmac(
            hash_name,
            password.encode("utf-8"),
            salt.encode("utf-8"),
            int(iterations),
        ).hex()
    except (ValueError, TypeError):
        return False
    return hmac.compare_digest(digest, expected)


def _b64encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode("ascii").rstrip("=")


def _b64decode(data: str) -> bytes:
    padding = "=" * (-len(data) % 4)
    return base64.urlsafe_b64decode(data + padding)


def _sign(payload: str) -> str:
    return _b64encode(hmac.new(_AUTH_SECRET, payload.encode("ascii"), hashlib.sha256).digest())


def create_access_token(user: User) -> str:
    payload = {
        "sub": user.username,
        "uid": user.id,
        "exp": int(time.time()) + _TOKEN_TTL_SECONDS,
    }
    encoded_payload = _b64encode(
        json.dumps(payload, separators=(",", ":")).encode("utf-8")
    )
    signature = _sign(encoded_payload)
    return f"{encoded_payload}.{signature}"


def _decode_token(token: str) -> dict[str, Any]:
    try:
        encoded_payload, signature = token.split(".", 1)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token.",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc

    expected_signature = _sign(encoded_payload)
    if not hmac.compare_digest(signature, expected_signature):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        payload = json.loads(_b64decode(encoded_payload))
    except (json.JSONDecodeError, ValueError) as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token.",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc
    if int(payload.get("exp", 0)) < int(time.time()):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication token expired.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return payload


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    app_db: Session = Depends(get_app_db),
) -> User:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    payload = _decode_token(credentials.credentials)
    user_id = payload.get("uid")
    user = app_db.get(User, user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User no longer exists.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user
