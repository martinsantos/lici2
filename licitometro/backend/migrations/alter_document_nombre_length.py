from alembic import op
import sqlalchemy as sa

def upgrade():
    # Alter the nombre column in documents table to varchar(255)
    op.alter_column('documents', 'nombre',
                    existing_type=sa.VARCHAR(length=50),
                    type_=sa.VARCHAR(length=255),
                    existing_nullable=True)

def downgrade():
    # Revert back to varchar(50) if needed
    op.alter_column('documents', 'nombre',
                    existing_type=sa.VARCHAR(length=255),
                    type_=sa.VARCHAR(length=50),
                    existing_nullable=True)
