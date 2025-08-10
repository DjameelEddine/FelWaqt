"""Create appointments table

Revision ID: 4f17a8fa7987
Revises: f0bd28a36601
Create Date: 2025-08-08 14:33:12.600761

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4f17a8fa7987'
down_revision: Union[str, Sequence[str], None] = 'f0bd28a36601'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "appointments",
        sa.Column("id", sa.Integer, primary_key=True, nullable=False),
        sa.Column("patient_id", sa.Integer, sa.ForeignKey("patients.id", ondelete="CASCADE")),
        sa.Column("doctor_id", sa.Integer, sa.ForeignKey("doctors.id", ondelete="CASCADE")),
        sa.Column("date", sa.Date, nullable=False),
        sa.Column("time", sa.Time(timezone=True), nullable=False),
        sa.Column("case", sa.String(20), nullable=False),
        sa.Column("done", sa.Boolean, nullable=False, server_default=sa.text("False")),
        sa.Column("confirmed", sa.Boolean, nullable=False, server_default=sa.text("False"))
    )

def downgrade() -> None:
    op.drop_table("appointments")
