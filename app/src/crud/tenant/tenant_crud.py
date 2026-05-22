from app.src.schemas.tenant.tenant_schema import (
    OrganisationCreate,
    BranchCreate,
)
from sqlalchemy.orm import Session
from app.src.models.tenant import Organisation, Branch


def create_organisation(db: Session, org: OrganisationCreate):
    existing = (
        db.query(Organisation).filter(Organisation.short_code == org.short_code).first()
    )
    if existing:
        raise RuntimeError(f"Organisation with code {org.short_code} already exists")

    db_org = Organisation(
        name=org.name,
        short_code=org.short_code,
        registration_no=org.registration_no,
        email=org.email,
        phone=org.phone,
        address=org.address,
        logo_url=org.logo_url,
        is_active=org.is_active,
        # settings
        default_currency=org.default_currency,
        min_share_value=org.min_share_value,
        loan_interest_rate=org.loan_interest_rate,
        savings_interest_rate=org.savings_interest_rate,
    )
    db.add(db_org)
    db.commit()
    db.refresh(db_org)
    return db_org


def create_branch(db: Session, branch: BranchCreate):
    db_branch = Branch(
        organisation_id=branch.organisation_id,
        branch_name=branch.branch_name,
        code=branch.code,
        location=branch.location,
        manager_name=branch.manager_name,
        branch_phone=branch.branch_phone,
        branch_email=branch.branch_email,
        is_active=branch.is_active,
    )
    db.add(db_branch)
    db.commit()
    db.refresh(db_branch)
    return db_branch

def get_branches(db:Session):
    branch = db.query(Branch).all()
    return branch
