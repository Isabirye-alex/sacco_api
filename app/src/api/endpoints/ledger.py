from datetime import date
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.src.config.database import get_db
from app.src.crud.ledger.ledger_crud import (
    create_chart_of_account,
    create_ledger_entry,
    create_ledger_line,
    create_journal_entry,
)
from app.src.models.ledger import (
    ChartOfAccount,
    LedgerEntry,
    LedgerLine,
    JournalEntry,
)
from app.src.schemas.ledger.ledger_schema import (
    ChartOfAccountCreate,
    ChartOfAccountResponse,
    LedgerEntryCreate,
    LedgerEntryResponse,
    LedgerLineCreate,
    LedgerLineResponse,
    JournalEntryCreate,
    JournalEntryResponse,
)

router = APIRouter()


@router.post(
    "/accounts",
    response_model=ChartOfAccountResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_chart_of_account_endpoint(
    account: ChartOfAccountCreate, db: Session = Depends(get_db)
):
    try:
        return create_chart_of_account(db, account)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error occurred: {e}",
        )


@router.get("/accounts", response_model=list[ChartOfAccountResponse])
def list_chart_of_accounts(db: Session = Depends(get_db)):
    return db.query(ChartOfAccount).all()


@router.post(
    "/entries",
    response_model=LedgerEntryResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_ledger_entry_endpoint(
    entry: LedgerEntryCreate, db: Session = Depends(get_db)
):
    try:
        return create_ledger_entry(db, entry)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error occurred: {e}",
        )


@router.get("/entries", response_model=list[LedgerEntryResponse])
def list_ledger_entries(db: Session = Depends(get_db)):
    return db.query(LedgerEntry).all()


@router.post(
    "/lines",
    response_model=LedgerLineResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_ledger_line_endpoint(line: LedgerLineCreate, db: Session = Depends(get_db)):
    try:
        return create_ledger_line(db, line)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error occurred: {e}",
        )


@router.get("/lines", response_model=list[LedgerLineResponse])
def list_ledger_lines(db: Session = Depends(get_db)):
    return db.query(LedgerLine).all()


@router.post(
    "/journals",
    response_model=JournalEntryResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_journal_entry_endpoint(
    journal: JournalEntryCreate, db: Session = Depends(get_db)
):
    try:
        return create_journal_entry(db, journal)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error occurred: {e}",
        )


@router.get("/journals", response_model=list[JournalEntryResponse])
def list_journal_entries(db: Session = Depends(get_db)):
    return db.query(JournalEntry).all()
