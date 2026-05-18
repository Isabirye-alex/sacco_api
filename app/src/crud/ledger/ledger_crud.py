from sqlalchemy.orm import Session

from app.src.models.ledger import ChartOfAccount, LedgerEntry, LedgerLine, JournalEntry
from app.src.schemas.ledger.ledger_schema import (
    ChartOfAccountCreate,
    LedgerEntryCreate,
    LedgerLineCreate,
    JournalEntryCreate,
)


def create_chart_of_account(db: Session, account: ChartOfAccountCreate):
    db_account = ChartOfAccount(
        organisation_id=account.organisation_id,
        code=account.code,
        name=account.name,
        account_type=account.account_type,
        account_category=account.account_category,
        parent_id=account.parent_id,
        description=account.description,
        is_active=account.is_active,
    )
    db.add(db_account)
    db.commit()
    db.refresh(db_account)
    return db_account


def create_ledger_entry(db: Session, entry: LedgerEntryCreate):
    db_entry = LedgerEntry(
        organisation_id=entry.organisation_id,
        branch_id=entry.branch_id,
        entry_no=entry.entry_no,
        entry_type=entry.entry_type,
        entry_date=entry.entry_date,
        description=entry.description,
        reference=entry.reference,
        total_debit=entry.total_debit,
        total_credit=entry.total_credit,
        status=entry.status,
        reversal_of_id=entry.reversal_of_id,
        created_by_id=entry.created_by_id,
        notes=entry.notes,
    )
    db.add(db_entry)
    db.commit()
    db.refresh(db_entry)
    return db_entry


def create_ledger_line(db: Session, line: LedgerLineCreate):
    db_line = LedgerLine(
        organisation_id=line.organisation_id,
        entry_id=line.entry_id,
        account_id=line.account_id,
        dr_cr=line.dr_cr,
        amount=line.amount,
        description=line.description,
        member_id=line.member_id,
    )
    db.add(db_line)
    db.commit()
    db.refresh(db_line)
    return db_line


def create_journal_entry(db: Session, journal: JournalEntryCreate):
    db_journal = JournalEntry(
        organisation_id=journal.organisation_id,
        branch_id=journal.branch_id,
        ledger_entry_id=journal.ledger_entry_id,
        narration=journal.narration,
        prepared_by_id=journal.prepared_by_id,
        approved_by_id=journal.approved_by_id,
        approved_date=journal.approved_date,
        is_approved=journal.is_approved,
    )
    db.add(db_journal)
    db.commit()
    db.refresh(db_journal)
    return db_journal
