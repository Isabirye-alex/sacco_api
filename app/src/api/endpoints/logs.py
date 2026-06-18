"""Endpoints for retrieving and recording authentication activity logs."""

from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.src.config.database import get_db
from app.src.crud.users.login_log_crud import (
    create_login_log,
    get_login_log_by_id,
    get_login_logs,
    get_login_logs_by_user,
)
from app.src.models.users.login_logs import LoginLogs
from app.src.schemas.users.login_log_schema import LoginLogCreate, LoginLogResponse

router = APIRouter()


def _extract_location_from_headers(
    request: Request, country: str | None = None, city: str | None = None
):
    """Resolve geographic context from request metadata when it was not provided."""
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


@router.get("/", response_model=List[LoginLogResponse])
def list_login_logs(db: Session = Depends(get_db)):
    """
    Retrieve all login log records.

    This endpoint returns the complete list of stored authentication events for
    auditing and support review. It is typically used by internal staff or admin
    tools that need a full activity history.

    Returns:
        A list of login log entries.
    """
    return get_login_logs(db)


@router.post("/", response_model=LoginLogResponse, status_code=status.HTTP_201_CREATED)
def save_login_log(
    log: LoginLogCreate, request: Request, db: Session = Depends(get_db)
):
    """
    Persist a new login activity record.

    The request body describes the event details, including status, attempts, and
    optional location fields. The endpoint captures request metadata such as the
    client IP address and user agent, then stores the record for later review.

    Returns:
        The created login log entry.

    Raises:
        HTTPException: If the record cannot be saved.
    """
    client_host = None
    if request.client:
        client_host = request.client.host

    ip_address = request.headers.get("x-forwarded-for", client_host)
    user_agent = request.headers.get("user-agent")

    location_country, location_city = _extract_location_from_headers(
        request, log.location_country, log.location_city
    )

    new_log = LoginLogs(
        user_id=log.user_id,
        ip_address=ip_address,
        user_agent=user_agent,
        status=log.status,
        failure_reason=log.failure_reason,
        attempts=log.attempts if log.attempts is not None else 1,
        session_id=log.session_id,
        location_country=location_country,
        location_city=location_city,
    )

    try:
        return create_login_log(db, new_log)
    except Exception:
        raise HTTPException(status_code=500, detail="Unable to save login log")


@router.get("/{log_id}", response_model=LoginLogResponse)
def get_login_log(log_id: UUID, db: Session = Depends(get_db)):
    """
    Fetch a single login log entry by identifier.

    This endpoint is useful when investigating a specific authentication event.
    If the requested record does not exist, the API returns a not-found error.

    Returns:
        The matching login log entry.

    Raises:
        HTTPException: If no log exists for the provided ID.
    """
    log = get_login_log_by_id(db, log_id)
    if not log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Login log not found"
        )
    return log


@router.get("/user/{user_id}", response_model=List[LoginLogResponse])
def list_login_logs_for_user(user_id: UUID, db: Session = Depends(get_db)):
    """
    Retrieve all login logs associated with a specific user.

    This is helpful for reviewing a user's authentication history, including both
    successful and failed attempts.

    Returns:
        A list of login events for the requested user.
    """
    return get_login_logs_by_user(db, user_id)
