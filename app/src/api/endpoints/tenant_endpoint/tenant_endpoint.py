from fastapi import APIRouter, HTTPException, status, Depends
from app.src.config.database import get_db
from app.src.schemas.tenant.tenant_schema import OrganisationCreate, OrganisationResponse
from sqlalchemy.orm import Session
from app.src.crud.tenant.tenant_crud import create_organisation

router = APIRouter()


@router.post("/org", response_model=OrganisationResponse, status_code=status.HTTP_201_CREATED)
def create_user(org: OrganisationCreate, db: Session = Depends(get_db)):
    try:
        return create_organisation(db, org)
    except Exception as e:
        print(f'Error debug {e}')
        raise HTTPException(status_code=500, detail=f'Internal server error occured with error reason {e}')
