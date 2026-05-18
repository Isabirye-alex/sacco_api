"""rename marital_status table and columns

Revision ID: ba7aea65df78
Revises: 565a56401396
Create Date: 2026-05-18 15:51:24.390411

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "ba7aea65df78"
down_revision: Union[str, Sequence[str], None] = "565a56401396"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.rename_table("marital_status", "marital_statuses")
    op.alter_column(
        "members",
        "marital_status",
        new_column_name="marital_status_id",
        existing_type=sa.UUID(),
        existing_nullable=True,
    )
    op.alter_column(
        "next_of_kin",
        "marital_status",
        new_column_name="marital_status_id",
        existing_type=sa.UUID(),
        existing_nullable=False,
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.alter_column(
        "next_of_kin",
        "marital_status_id",
        new_column_name="marital_status",
        existing_type=sa.UUID(),
        existing_nullable=False,
    )
    op.alter_column(
        "members",
        "marital_status_id",
        new_column_name="marital_status",
        existing_type=sa.UUID(),
        existing_nullable=True,
    )
    op.rename_table("marital_statuses", "marital_status")
