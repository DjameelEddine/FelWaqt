"""Create patients table

Revision ID: 4f418aece559
Revises: 
Create Date: 2025-08-08 14:18:30.552470

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4f418aece559'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "patients",
        sa.Column("id", sa.Integer, primary_key=True, nullable=False),
        sa.Column("first_name", sa.String, nullable=False),
        sa.Column("last_name", sa.String, nullable=False),
        sa.Column("email", sa.String, unique=True, nullable=False),
        sa.Column("phone", sa.String(15), unique=True, nullable=False),
        sa.Column("role", sa.String, nullable=False, server_default="patient"),
        sa.Column("password", sa.String, nullable=False)
    )

def downgrade() -> None:
    op.drop_table("patients")