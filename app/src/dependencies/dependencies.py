"""
app/src/auth/dependencies.py
=============================
FastAPI dependency functions for authentication and role-based access control.

Two-layer check
---------------
1. user_type  — is this a MEMBER or STAFF account?  (structural gate)
2. role.role  — what specific permissions does this staff member have?

Usage in routes
---------------
    from app.src.auth.dependencies import (
        get_current_user,
        require_member,
        require_staff,
        require_roles,
    )

    # any authenticated user
    @router.get("/me")
    def get_me(user: User = Depends(get_current_user)): ...

    # members only (their own portal)
    @router.get("/my-savings")
    def my_savings(user: User = Depends(require_member)): ...

    # any staff
    @router.get("/members")
    def list_members(user: User = Depends(require_staff)): ...

    # specific role(s)
    @router.post("/loans/{id}/approve")
    def approve_loan(user: User = Depends(require_roles("LOAN_OFFICER", "BRANCH_MANAGER", "ADMIN"))): ...

    # admin or above
    @router.delete("/members/{id}")
    def delete_member(user: User = Depends(require_admin)): ...
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
import jwt

from app.src.models.member import User
from app.src.config.database import get_db 
from app.src.config.settings import settings 

bearer_scheme = HTTPBearer()


# Token extraction


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    """
    Decode the JWT, look up the user, and return it.
    Raises 401 for any token or lookup failure.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            credentials.credentials,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception

    user = db.query(User).filter(User.id == user_id, User.is_deleted == False).first()

    if user is None:
        raise credentials_exception
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is deactivated.",
        )
    if not user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is not verified. Check your email.",
        )
    return user


#Layer 1: user_type gate 


def require_member(current_user: User = Depends(get_current_user)) -> User:
    """
    Allow only MEMBER-type users (regular portal access).
    Blocks all staff accounts even if they somehow hit a member route.
    """
    if not current_user.is_member_user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Member account required.",
        )
    return current_user


def require_staff(current_user: User = Depends(get_current_user)) -> User:
    """
    Allow only STAFF-type users.
    Blocks all member accounts from staff routes.
    """
    if not current_user.is_staff_user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Staff account required.",
        )
    return current_user


# Layer 2: role gate

def require_roles(*roles: str):
    """
    Factory — returns a dependency that allows only staff with one of
    the specified roles.  Always enforces is_staff_user first.

    Usage:
        Depends(require_roles("TREASURER", "ADMIN"))
    """

    def checker(current_user: User = Depends(require_staff)) -> User:
        if not current_user.has_role(*roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Required role(s): {', '.join(roles)}.",
            )
        return current_user

    return checker


def require_admin(current_user: User = Depends(require_staff)) -> User:
    """Allow only ADMIN or SUPER_ADMIN."""
    if not current_user.is_admin_or_above():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required.",
        )
    return current_user


def require_super_admin(current_user: User = Depends(require_staff)) -> User:
    """Allow only SUPER_ADMIN (platform-level operations)."""
    if not current_user.has_role("SUPER_ADMIN"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Super admin access required.",
        )
    return current_user
