"""Security utilities for JWT handling and request authentication."""

from __future__ import annotations

import hashlib
from collections.abc import Callable
from datetime import datetime, timedelta, timezone

from fastapi import Depends, HTTPException, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from passlib.context import CryptContext

from .settings import get_settings


token_scheme = HTTPBearer(auto_error=False)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def hash_identifier(value: str, salt: str) -> str:
    return hashlib.sha256(f"{salt}:{value}".encode("utf-8")).hexdigest()


def create_access_token(
    subject: str,
    expires_delta: timedelta | None = None,
    roles: list[str] | None = None,
) -> str:
    settings = get_settings()
    expire = datetime.now(tz=timezone.utc) + (
        expires_delta or timedelta(minutes=settings.access_token_expire_minutes)
    )
    payload = {"sub": subject, "exp": expire, "iat": datetime.now(tz=timezone.utc)}
    if roles:
        payload["roles"] = roles
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def decode_token(token: str) -> dict:
    settings = get_settings()
    return jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])


def verify_token(creds: HTTPAuthorizationCredentials | None = Security(token_scheme)) -> str:
    if creds is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing token")
    token = creds.credentials
    try:
        decode_token(token)
    except JWTError as exc:  # pragma: no cover - FastAPI handles HTTPException path
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid token") from exc
    return token


def get_current_user(token: str = Depends(verify_token)) -> dict:
    payload = decode_token(token)
    subject = payload.get("sub")
    if not isinstance(subject, str) or not subject.strip():
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid token claims")

    raw_roles = payload.get("roles", [])
    if raw_roles is None:
        roles: list[str] = []
    elif isinstance(raw_roles, list) and all(isinstance(role, str) for role in raw_roles):
        roles = raw_roles
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid token claims")

    return {"sub": subject, "issued_at": payload.get("iat"), "roles": roles}


def require_roles(*required_roles: str) -> Callable:
    required = set(required_roles)

    def _enforce_roles(user: dict = Depends(get_current_user)) -> dict:
        user_roles = user.get("roles", [])
        if not isinstance(user_roles, list):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient role")
        if required and not required.intersection(set(user_roles)):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient role")
        return user

    return _enforce_roles
