import hashlib
import secrets
from datetime import datetime, timedelta, timezone

import jwt

from app.src.config.settings import settings


def hash_password(password: str) -> str:
  """Hash a password using PBKDF2-HMAC-SHA256 with a random salt."""
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


def create_access_token(subject: str, expires_minutes: int = 60) -> str:
  expire = datetime.now(timezone.utc) + timedelta(minutes=expires_minutes)
  payload = {"sub": subject, "exp": expire}
  return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
