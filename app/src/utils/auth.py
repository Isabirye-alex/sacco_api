"""Module for app.src.utils.auth."""

import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from fastapi import Depends, HTTPException, Header, status
import jwt
from app.src.config.settings import settings

from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.src.config.settings import settings

# This tells FastAPI to expect standard 'Authorization: Bearer <token>' headers
security = HTTPBearer()


SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = 30


def hash_password(password: str) -> str:
    """Hash a password using PBKDF2-HMAC-SHA256 with a random salt.

    Returns a string in the format: salt$hexhash
    """
    salt = secrets.token_hex(16)
    dk = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 100_000)
    return f"{salt}${dk.hex()}"


def verify_password(password: str, hashed: str) -> bool:
    try:
        salt, hexhash = hashed.split("$", 1)
    except ValueError:
        return False
    dk = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 100_000)
    return secrets.compare_digest(dk.hex(), hexhash)


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def get_user_id_from_token(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> str:
    """
    Decodes the token and returns the user_id (stored in 'sub').
    """
    token = credentials.credentials
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        user_id: str = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload: missing User ID",
            )
        return user_id
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session expired. Please log in again.",
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token.",
        )


def get_member_id_from_token(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> str:
    """
    Decodes the incoming standard Authorization Bearer token and returns the member_id.
    """
    token = credentials.credentials

    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )

        member_id: str = payload.get("member_id")
        if not member_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload: missing member ID",
            )

        return member_id

    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session expired. Please log in again.",
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token.",
        )
