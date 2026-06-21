"""Module for app.src.api.endpoints.member."""

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
    get_current_member
)
from app.src.models.member import (
    Gender,
    MemberStatus,
    MaritalStatus,
    Role,
    NextOfKin,
)
from app.src.schemas.member.member_schema import (
    CombinedMemberResponse,
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
from app.src.schemas.users.user_schema import UserCreate
from app.src.utils.auth import get_member_id_from_token

router = APIRouter()


# Set up logging instead of using print statements
logger = logging.getLogger(__name__)


@router.post("/", response_model=MemberResponse, status_code=status.HTTP_201_CREATED)
def create_member_endpoint(member: MemberCreate,user: UserCreate ,db: Session = Depends(get_db)):
    """
    Register a new member and create the related user account.

    This endpoint accepts the member profile payload and the initial user credentials,
    validates the input, and stores both records together so the new member can log in
    immediately after registration.

    Returns the created member record in the response body.
    """
    try:
        return create_member(db, member, user)

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
            detail=f"An unexpected internal system error occurred. Please try again later. {e}",
        )


@router.post(
    "/genders", response_model=GenderResponse, status_code=status.HTTP_201_CREATED
)
def create_gender_endpoint(gender: GenderCreate, db: Session = Depends(get_db)):
    """
    Create a new gender lookup entry.

    Use this endpoint to add a permitted gender option to the system lookup data.
    The value is stored as a reference record and can later be used by member forms,
    filters, and reporting.
    """
    try:
        return create_gender(db, gender)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error occurred: {e}",
        )


@router.get("/genders", response_model=list[GenderResponse])
def list_genders(db: Session = Depends(get_db)):
    """
    Retrieve all available gender values.

    This endpoint returns the lookup table used to populate dropdowns and validation lists
    for member registration and profile updates.
    """
    return db.query(Gender).all()


@router.post(
    "/member-statuses",
    response_model=MemberStatusResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_member_status_endpoint(
    member_status: MemberStatusCreate, db: Session = Depends(get_db)
):
    """
    Create a new member status lookup record.

    This endpoint allows administrators to define status options such as Active,
    Pending, Suspended, or Exited for member lifecycle tracking.
    """
    try:
        return create_member_status(db, member_status)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error occurred: {e}",
        )


@router.get("/member-statuses", response_model=list[MemberStatusResponse])
def list_member_statuses(db: Session = Depends(get_db)):
    """
    Retrieve all member status values.

    The returned records are used by the application to surface the available lifecycle
    states for members and to support search and filtering in admin screens.
    """
    return db.query(MemberStatus).all()


@router.post(
    "/marital-statuses",
    response_model=MaritalStatusResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_marital_status_endpoint(
    marital_status: MaritalStatusCreate, db: Session = Depends(get_db)
):
    """
    Create a new marital status lookup value.

    This endpoint stores the allowable marital options for member records and profile forms.
    """
    try:
        return create_marital_status(db, marital_status)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error occurred: {e}",
        )


@router.get("/marital-statuses", response_model=list[MaritalStatusResponse])
def list_marital_statuses(db: Session = Depends(get_db)):
    """
    Retrieve all marital status values.

    This endpoint is typically used to populate forms and filters that ask for the
    member's marital background.
    """
    return db.query(MaritalStatus).all()


@router.post("/roles", response_model=RoleResponse, status_code=status.HTTP_201_CREATED)
def create_role_endpoint(role: RoleCreate, db: Session = Depends(get_db)):
    """
    Create a new role definition in the system.

    Use this endpoint to add access roles or organizational responsibilities that can be
    assigned to staff and members throughout the platform.
    """
    try:
        return create_role(db, role)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error occurred: {e}",
        )


@router.get("/roles", response_model=list[RoleResponse])
def list_roles(db: Session = Depends(get_db)):
    """
    Retrieve all available roles.

    This endpoint returns the lookup records used by authorization logic, admin tools,
    and UI role-selection components.
    """
    return db.query(Role).all()


@router.post(
    "/next-of-kin",
    response_model=NextOfKinResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_next_of_kin_endpoint(kin: NextOfKinCreate, db: Session = Depends(get_db)):
    """
    Create a next-of-kin record for a member.

    This endpoint stores emergency contact information that may be needed for member
    verification, support workflows, and operational follow-up.
    """
    try:
        return create_next_of_kin(db, kin)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error occurred: {e}",
        )


@router.get("/next-of-kin", response_model=list[NextOfKinResponse])
def list_next_of_kin(db: Session = Depends(get_db)):
    """
    Retrieve all next-of-kin records.

    This endpoint is helpful for admin review, emergency contact lookups, and member
    support operations.
    """
    return db.query(NextOfKin).all()


@router.get('/member/', response_model=CombinedMemberResponse, status_code=status.HTTP_200_OK)
def get_member_data(
    db: Session = Depends(get_db), 
    member_id: str = Depends(get_member_id_from_token) # Token is decoded automatically right here!
):
    """
    Retrieve the authenticated member's full profile.

    The token is used to determine which member is making the request, and the response
    returns the complete member profile data needed by dashboards, profile pages, and
    account management workflows.
    """
    try:
        member_data = get_current_member(db, member_id)
        if not member_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="Member profile not found"
            )
        return member_data
        
    except HTTPException:
        raise  
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Database error: {str(e)}"
        )