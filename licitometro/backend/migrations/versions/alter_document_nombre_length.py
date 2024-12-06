"""alter document nombre length

Revision ID: alter_document_nombre_length
Revises: 
Create Date: 2024-02-12 22:59:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'alter_document_nombre_length'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Use raw SQL to alter the column length
    op.execute('ALTER TABLE documents ALTER COLUMN nombre TYPE varchar(255);')


def downgrade() -> None:
    # Revert back to varchar(50) if needed
    op.execute('ALTER TABLE documents ALTER COLUMN nombre TYPE varchar(50);')
