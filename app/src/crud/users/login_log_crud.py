from typing import List
from uuid import UUID

from sqlalchemy.orm import Session

from app.src.models.users.login_logs import LoginLogs


def get_login_logs(db: Session) -> List[LoginLogs]:
    return db.query(LoginLogs).order_by(LoginLogs.login_at.desc()).all()


def get_login_logs_by_user(db: Session, user_id: UUID) -> List[LoginLogs]:
    return (
        db.query(LoginLogs)
        .filter(LoginLogs.user_id == user_id)
        .order_by(LoginLogs.login_at.desc())
        .all()
    )


def get_login_attempt_count(db: Session, user_id: UUID) -> int:
    last_success = (
        db.query(LoginLogs)
        .filter(LoginLogs.user_id == user_id, LoginLogs.status == "success")
        .order_by(LoginLogs.login_at.desc())
        .first()
    )
    if not last_success:
        return (
            db.query(LoginLogs)
            .filter(LoginLogs.user_id == user_id, LoginLogs.status == "failure")
            .count()
        )
    return (
        db.query(LoginLogs)
        .filter(
            LoginLogs.user_id == user_id,
            LoginLogs.status == "failure",
            LoginLogs.login_at > last_success.login_at,
        )
        .count()
    )


def get_login_log_by_id(db: Session, log_id: UUID) -> LoginLogs | None:
    return db.query(LoginLogs).filter(LoginLogs.log_id == log_id).first()


def create_login_log(db: Session, log_data: LoginLogs) -> LoginLogs:
    try:
        db.add(log_data)
        db.commit()
        db.refresh(log_data)
        return log_data
    except Exception:
        db.rollback()
        raise
