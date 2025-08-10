"""Create reschedules table

Revision ID: fbdaa4dee7fc
Revises: 4f17a8fa7987
Create Date: 2025-08-08 14:34:01.650740

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'fbdaa4dee7fc'
down_revision: Union[str, Sequence[str], None] = '4f17a8fa7987'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "reschedules",
        sa.Column("appointment_id", sa.Integer, sa.ForeignKey("appointments.id", ondelete="CASCADE"), primary_key=True, nullable=False),
        sa.Column("old_date", sa.Date, nullable=False),
        sa.Column("old_time", sa.Time, nullable=False),
        sa.Column("new_date", sa.Date, nullable=False),
        sa.Column("new_time", sa.Time, nullable=False)
    )

def downgrade() -> None:
    op.drop_table("reschedules")
