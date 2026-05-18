"""
seeds/lookups.py
=================
Seeds all admin-managed lookup tables that back the Member & Auth models.

Call seed_lookups(db) once on application startup (it is idempotent).
Call seed_default_roles(db) as part of the same startup sequence.

These are global tables (not per-organisation) so they are seeded once
for the whole platform.
"""

from sqlalchemy.orm import Session

from app.src.models.member import Gender, MemberStatus, MaritalStatus, Role


# Roles

_ROLES = [
    {
        "role": "MEMBER",
        "description": "Regular SACCO member — portal access only.",
        "is_system": True,
    },
    {
        "role": "LOAN_OFFICER",
        "description": "Reviews and processes loan applications.",
        "is_system": True,
    },
    {
        "role": "TREASURER",
        "description": "Full access to savings, shares, and the ledger.",
        "is_system": True,
    },
    {
        "role": "BRANCH_MANAGER",
        "description": "Manages all operations within a single branch.",
        "is_system": True,
    },
    {
        "role": "ADMIN",
        "description": "Organisation-wide administration.",
        "is_system": True,
    },
    {
        "role": "SUPER_ADMIN",
        "description": "Platform-level access across all organisations.",
        "is_system": True,
    },
]


# Gender 
_GENDERS = [
    {"gender": "Male",             "description": None},
    {"gender": "Female",           "description": None},
    {"gender": "Other",            "description": None},
    {"gender": "Prefer not to say","description": None},
]


# ─── Member Status ────────────────────────────────────────────────────────────

_MEMBER_STATUSES = [
    {"status": "Pending",   "description": "Application submitted, awaiting approval."},
    {"status": "Active",    "description": "Fully registered and active member."},
    {"status": "Dormant",   "description": "No account activity for more than 6 months."},
    {"status": "Suspended", "description": "Temporarily suspended pending investigation."},
    {"status": "Exited",    "description": "Member has voluntarily withdrawn from the SACCO."},
]


# ─── Marital Status ───────────────────────────────────────────────────────────

_MARITAL_STATUSES = [
    {"status": "Single",    "description": None},
    {"status": "Married",   "description": None},
    {"status": "Widowed",   "description": None},
    {"status": "Divorced",  "description": None},
    {"status": "Separated", "description": None},
]


# ─── Seed functions ───────────────────────────────────────────────────────────

def seed_roles(db: Session) -> None:
    """Insert system roles if they don't exist. Safe to call multiple times."""
    existing = {r.role for r in db.query(Role).all()}
    for row in _ROLES:
        if row["role"] not in existing:
            db.add(Role(**row))
    db.commit()


def seed_genders(db: Session) -> None:
    existing = {g.gender for g in db.query(Gender).all()}
    for row in _GENDERS:
        if row["gender"] not in existing:
            db.add(Gender(**row))
    db.commit()


def seed_member_statuses(db: Session) -> None:
    existing = {s.status for s in db.query(MemberStatus).all()}
    for row in _MEMBER_STATUSES:
        if row["status"] not in existing:
            db.add(MemberStatus(**row))
    db.commit()


def seed_marital_statuses(db: Session) -> None:
    existing = {s.status for s in db.query(MaritalStatus).all()}
    for row in _MARITAL_STATUSES:
        if row["status"] not in existing:
            db.add(MaritalStatus(**row))
    db.commit()


def seed_lookups(db: Session) -> None:
    """
    Convenience function — seeds all lookup tables in one call.
    Call this on application startup before anything else.

    Usage in main.py:
        @app.on_event("startup")
        def startup():
            db = next(get_db())
            seed_lookups(db)
    """
    seed_roles(db)
    seed_genders(db)
    seed_member_statuses(db)
    seed_marital_statuses(db)