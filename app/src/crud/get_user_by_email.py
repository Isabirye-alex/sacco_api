from sqlalchemy.orm import Session
from app.src.models.users.user_model import UserModel

def get_user_by_email(db: Session, email):
    user = db.query(UserModel).filter(UserModel.email == email).first()
    return user