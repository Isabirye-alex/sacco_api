"""Authentication endpoints for sign-in, token issuance, and login auditing."""

import logging

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.src.config.database import get_db
from app.src.crud.get_user_by_email import get_user_by_email
from app.src.crud.users.login_log_crud import create_login_log, get_login_attempt_count
from app.src.models.users.login_logs import LoginLogs
from app.src.schemas.users.user_schema import UserResponse, UserSignIn
from app.src.utils.auth import (
    verify_password,
    create_access_token,
)

logger = logging.getLogger(__name__)

router = APIRouter()


def _extract_location(
    request: Request, country: str | None = None, city: str | None = None
):
    """Resolve location data from request headers when it is not supplied explicitly."""
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


@router.post("/signin")
def signin(auth: UserSignIn, request: Request, db: Session = Depends(get_db)):
    """
    Authenticate a user and issue a JWT access token.

    The request body carries the user's credentials and optional location hints.
    After validating the email/password combination, the endpoint records the
    outcome in the login log table and returns a bearer token for subsequent API
    calls. Failed attempts are also logged so they can be reviewed by support staff.

    Raises:
        HTTPException: If the supplied credentials are invalid or the login cannot
            be recorded.

    Returns:
        A token response containing the access token and token type.
    """
    try:
        logger.info(
            "Signin request received for email=%s",
            auth.email,
        )

        user = get_user_by_email(db, auth.email)
        logger.info(
            "User lookup result for email=%s: %s",
            auth.email,
            user is not None,
        )

        failed_attempts = 0
        if user:
            failed_attempts = get_login_attempt_count(db, user.id)  # type: ignore

        location_country, location_city = _extract_location(
            request, auth.location_country, auth.location_city
        )

        if not user or not verify_password(auth.password, user.hashed_password):
            attempt_count = failed_attempts + 1
            log_entry = LoginLogs(
                member_id=user.member_id if user else None,
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
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
            )

        attempt_count = 1
        log_entry = LoginLogs(
            user_id=user.id,
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
        logger.info(
            "Recording successful login attempt for user_id=%s",
            user.id,
        )
        try:
            create_login_log(db, log_entry)
            logger.info(
                "Login audit entry created successfully for user_id=%s",
                user.id,
            )
        except Exception as exc:
            logger.exception(
                "Failed to create login audit entry for user_id=%s",
                user.id,
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Could not record login audit",
            ) from exc

        token_payload = {  # type: ignore
            "sub": str(user.id),
            "member_id": str(user.member_id) if user.member_id else None,
        }

        logger.info(
            "Attempting to generate access token for user_id=%s",
            user.id,
        )

        try:
            access_token = create_access_token(data=token_payload)
            logger.info(
                "Access token generated successfully for user_id=%s",
                user.id,
            )
        except Exception as exc:
            logger.exception(
                "Failed to generate access token for user_id=%s",
                user.id,
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Could not generate access token",
            ) from exc

        return {"access_token": access_token, "token_type": "bearer"}
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception(
            "Unexpected exception during signin for email=%s",
            auth.email,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during sign-in",
        ) from exc
