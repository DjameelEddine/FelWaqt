"""Create feedbacks table

Revision ID: 3c8d0c23aeb2
Revises: fbdaa4dee7fc
Create Date: 2025-08-08 14:34:39.183072

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3c8d0c23aeb2'
down_revision: Union[str, Sequence[str], None] = 'fbdaa4dee7fc'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "feedbacks",
        sa.Column("appointment_id", sa.Integer, sa.ForeignKey("appointments.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("rating", sa.Integer),
        sa.Column("plain", sa.String(200), nullable=False)
    )

def downgrade() -> None:
    op.drop_table("feedbacks")
