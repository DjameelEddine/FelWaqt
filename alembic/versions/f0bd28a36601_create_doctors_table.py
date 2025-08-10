"""Create doctors table

Revision ID: f0bd28a36601
Revises: 4f418aece559
Create Date: 2025-08-08 14:32:49.086481

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f0bd28a36601'
down_revision: Union[str, Sequence[str], None] = '4f418aece559'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "doctors",
        sa.Column("id", sa.Integer, primary_key=True, nullable=False),
        sa.Column("first_name", sa.String, nullable=False),
        sa.Column("last_name", sa.String, nullable=False),
        sa.Column("email", sa.String, unique=True, nullable=False),
        sa.Column("phone", sa.String(15), unique=True, nullable=False),
        sa.Column("specialty", sa.String, nullable=False),
        sa.Column("city", sa.String(50), nullable=False),
        sa.Column("street", sa.String(50), nullable=False),
        sa.Column("postal_code", sa.String(10), nullable=False),
        sa.Column("personal_picture", sa.String(200), unique=True),
        sa.Column("role", sa.String, nullable=False, server_default="doctor"),
        sa.Column("password", sa.String, nullable=False)
    )

def downgrade() -> None:
    op.drop_table("doctors")