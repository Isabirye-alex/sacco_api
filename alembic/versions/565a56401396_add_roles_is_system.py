"""add roles is_system

Revision ID: 565a56401396
Revises: b21ead29a998
Create Date: 2026-05-18 15:49:25.797821

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "565a56401396"
down_revision: Union[str, Sequence[str], None] = "b21ead29a998"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "roles",
        sa.Column(
            "is_system",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
        ),
    )
    op.alter_column("roles", "is_system", server_default=None)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("roles", "is_system")
