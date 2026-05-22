from typing import List

from fastapi import APIRouter, HTTPException, status, Depends
from app.src.config.database import get_db
from app.src.schemas.tenant.tenant_schema import (
    OrganisationCreate,
    OrganisationResponse,
    BranchCreate,
    BranchResponse,
)
from sqlalchemy.orm import Session
from app.src.crud.tenant.tenant_crud import create_organisation, create_branch, get_branches

router = APIRouter()


@router.post(
    "/org", response_model=OrganisationResponse, status_code=status.HTTP_201_CREATED
)
def create_user(org: OrganisationCreate, db: Session = Depends(get_db)):
    try:
        return create_organisation(db, org)
    except Exception as e:
        print(f"Error debug {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error occured with error reason {e}",
        )


@router.post(
    "/branch", response_model=BranchResponse, status_code=status.HTTP_201_CREATED
)
def create_branch_endpoint(branch: BranchCreate, db: Session = Depends(get_db)):
    try:
        return create_branch(db, branch)
    except Exception as e:
        print(f"Error debug {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error occured with error reason {e}",
        )

@router.get('/branches', response_model=List[BranchResponse], status_code=status.HTTP_200_OK)
def get_all_branches(db:Session=Depends(get_db)):
    try:
        return get_branches(db)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f'Unexpected error occured : {e}')