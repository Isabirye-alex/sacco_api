from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.src.config.database import get_db
from app.src.crud.get_user_by_email import get_user_by_email
from app.src.crud.users.login_log_crud import create_login_log, get_login_attempt_count
from app.src.models.users.login_logs import LoginLogs
from app.src.schemas.users.user_schema import UserResponse, UserSignIn
from app.src.utils.auth import verify_password

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


@router.post("/signin", response_model=UserResponse)
def signin(auth: UserSignIn, request: Request, db: Session = Depends(get_db)):
    user = get_user_by_email(db, auth.email)
    failed_attempts = 0
    if user:
        failed_attempts = get_login_attempt_count(db, user.user_id)

    location_country, location_city = _extract_location(
        request, auth.location_country, auth.location_city
    )

    if not user or not verify_password(auth.password, user.password):
        attempt_count = failed_attempts + 1
        log_entry = LoginLogs(
            user_id=user.user_id if user else None,
            ip_address=request.headers.get(
                "x-forwarded-for", request.client.host if request.client else None
            ),
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

    attempt_count = 1
    log_entry = LoginLogs(
        user_id=user.user_id,
        ip_address=request.headers.get(
            "x-forwarded-for", request.client.host if request.client else None
        ),
        user_agent=request.headers.get("user-agent"),
        status="success",
        failure_reason=None,
        attempts=attempt_count,
        session_id=None,
        location_country=location_country,
        location_city=location_city,
    )
    create_login_log(db, log_entry)

    return user
