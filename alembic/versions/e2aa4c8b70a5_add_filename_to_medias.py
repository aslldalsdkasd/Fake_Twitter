"""add filename to medias

Revision ID: e2aa4c8b70a5
Revises: 
Create Date: 2026-03-21 01:21:36.335706

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e2aa4c8b70a5'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None
from alembic import op
import sqlalchemy as sa

def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "medias",
        sa.Column("filename", sa.String(500), nullable=False)
    )


    op.add_column(
        "medias",
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"))
    )

def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("medias", "created_at")
    op.drop_column("medias", "filename")