from sqlalchemy.orm import Session

from app.src.models.member import User


def get_user_by_email(db: Session, email: str, organisation_id=None):
  query = db.query(User).filter(User.email == email)
  if organisation_id is not None:
    query = query.filter(User.organisation_id == organisation_id)
  return query.first()


def get_user_by_id(db: Session, user_id):
  return db.query(User).filter(User.id == user_id).first()
