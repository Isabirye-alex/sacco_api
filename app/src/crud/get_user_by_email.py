"""Module for app.src.crud.get_user_by_email."""

from sqlalchemy.orm import Session
from app.src.models.member import User


def get_user_by_email(db: Session, email): # type: ignore
    user = db.query(User).filter(User.email == email).first() # type: ignore
    return user
