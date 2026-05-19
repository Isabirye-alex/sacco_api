from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import logging

from app.src.config.database import get_db
from app.src.crud.member.member_crud import (
    create_member,
    create_gender,
    create_member_status,
    create_marital_status,
    create_role,
    create_next_of_kin,
)
from app.src.models.member import (
    Gender,
    MemberStatus,
    MaritalStatus,
    Role,
    NextOfKin,
)
from app.src.schemas.member.member_schema import (
    MemberCreate,
    MemberResponse,
    GenderCreate,
    GenderResponse,
    MemberStatusCreate,
    MemberStatusResponse,
    MaritalStatusCreate,
    MaritalStatusResponse,
    RoleCreate,
    RoleResponse,
    NextOfKinCreate,
    NextOfKinResponse,
)

router = APIRouter()


# Set up logging instead of using print statements
logger = logging.getLogger(__name__)


@router.post("/", response_model=MemberResponse, status_code=status.HTTP_201_CREATED)
def create_member_endpoint(member: MemberCreate, db: Session = Depends(get_db)):
    try:
        return create_member(db, member)

    except HTTPException as http_ex:
        raise http_ex

    except Exception as e:
        # Log the detailed traceback securely on the backend server
        logger.error(
            f"Unexpected system crash during member creation: {e}", exc_info=True
        )

        # Do not expose raw database errors or tracebacks to the API customer
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected internal system error occurred. Please try again later.",
        )


@router.post(
    "/genders", response_model=GenderResponse, status_code=status.HTTP_201_CREATED
)
def create_gender_endpoint(gender: GenderCreate, db: Session = Depends(get_db)):
    try:
        return create_gender(db, gender)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error occurred: {e}",
        )


@router.get("/genders", response_model=list[GenderResponse])
def list_genders(db: Session = Depends(get_db)):
    return db.query(Gender).all()


@router.post(
    "/member-statuses",
    response_model=MemberStatusResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_member_status_endpoint(
    status: MemberStatusCreate, db: Session = Depends(get_db)
):
    try:
        return create_member_status(db, status)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error occurred: {e}",
        )


@router.get("/member-statuses", response_model=list[MemberStatusResponse])
def list_member_statuses(db: Session = Depends(get_db)):
    return db.query(MemberStatus).all()


@router.post(
    "/marital-statuses",
    response_model=MaritalStatusResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_marital_status_endpoint(
    status: MaritalStatusCreate, db: Session = Depends(get_db)
):
    try:
        return create_marital_status(db, status)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error occurred: {e}",
        )


@router.get("/marital-statuses", response_model=list[MaritalStatusResponse])
def list_marital_statuses(db: Session = Depends(get_db)):
    return db.query(MaritalStatus).all()


@router.post("/roles", response_model=RoleResponse, status_code=status.HTTP_201_CREATED)
def create_role_endpoint(role: RoleCreate, db: Session = Depends(get_db)):
    try:
        return create_role(db, role)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error occurred: {e}",
        )


@router.get("/roles", response_model=list[RoleResponse])
def list_roles(db: Session = Depends(get_db)):
    return db.query(Role).all()


@router.post(
    "/next-of-kin",
    response_model=NextOfKinResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_next_of_kin_endpoint(kin: NextOfKinCreate, db: Session = Depends(get_db)):
    try:
        return create_next_of_kin(db, kin)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error occurred: {e}",
        )


@router.get("/next-of-kin", response_model=list[NextOfKinResponse])
def list_next_of_kin(db: Session = Depends(get_db)):
    return db.query(NextOfKin).all()
