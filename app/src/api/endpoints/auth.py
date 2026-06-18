from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.src.config.database import get_db
from app.src.crud.get_user_by_email import get_user_by_email
from app.src.crud.users.login_log_crud import create_login_log, get_login_attempt_count
from app.src.crud.users.user_create_crud import _to_user_response
from app.src.models.users.login_logs import LoginLogs
from app.src.schemas.users.user_schema import TokenResponse, UserSignIn
from app.src.utils.auth import create_access_token, verify_password

router = APIRouter()


def _extract_location(
  request: Request, country: str | None = None, city: str | None = None
):
  if country:
    resolved_country = country
  else:
    resolved_country = (
      request.headers.get("cf-ipcountry")
      or request.headers.get("x-country")
      or request.headers.get("x-appengine-country")
      or request.headers.get("x-region")
      or None
    )

  if city:
    resolved_city = city
  else:
    resolved_city = (
      request.headers.get("x-geo-city")
      or request.headers.get("x-city")
      or request.headers.get("x-region")
      or None
    )

  return resolved_country, resolved_city


def _client_ip(request: Request) -> str | None:
  return request.headers.get(
    "x-forwarded-for", request.client.host if request.client else None
  )


@router.post("/signin", response_model=TokenResponse)
def signin(auth: UserSignIn, request: Request, db: Session = Depends(get_db)):
  user = get_user_by_email(db, auth.email)
  member_id = user.member_id if user else None
  failed_attempts = get_login_attempt_count(db, member_id) if member_id else 0

  location_country, location_city = _extract_location(
    request, auth.location_country, auth.location_city
  )

  if not user or not verify_password(auth.password, user.hashed_password):
    attempt_count = failed_attempts + 1
    log_entry = LoginLogs(
      member_id=member_id,
      ip_address=_client_ip(request),
      user_agent=request.headers.get("user-agent"),
      status="failure",
      failure_reason="Invalid credentials",
      attempts=attempt_count,
      session_id=None,
      location_country=location_country,
      location_city=location_city,
    )
    create_login_log(db, log_entry)
    raise HTTPException(
      status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password"
    )

  if not user.is_active:
    raise HTTPException(
      status_code=status.HTTP_403_FORBIDDEN, detail="Account is deactivated"
    )

  log_entry = LoginLogs(
    member_id=user.member_id,
    ip_address=_client_ip(request),
    user_agent=request.headers.get("user-agent"),
    status="success",
    failure_reason=None,
    attempts=1,
    session_id=None,
    location_country=location_country,
    location_city=location_city,
  )
  create_login_log(db, log_entry)

  token = create_access_token(str(user.id))
  return TokenResponse(access_token=token, user=_to_user_response(user))
