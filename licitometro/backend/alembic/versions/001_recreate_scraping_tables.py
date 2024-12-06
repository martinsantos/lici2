"""Recreate scraping tables

Revision ID: 001
Revises: 
Create Date: 2024-01-20 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import func


# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Create scraping_templates table
    op.create_table(
        'scraping_templates_new',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('description', sa.String(), nullable=True),
        sa.Column('url', sa.String(), nullable=False),
        sa.Column('fields', sa.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_scraping_templates_new_id'), 'scraping_templates_new', ['id'], unique=False)
    op.create_index(op.f('ix_scraping_templates_new_name'), 'scraping_templates_new', ['name'], unique=True)
    
    # Create scraping_jobs table
    op.create_table(
        'scraping_jobs_new',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('template_id', sa.Integer(), nullable=True),
        sa.Column('status', sa.String(), nullable=True),
        sa.Column('started_at', sa.DateTime(), nullable=True),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('result', sa.JSON(), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('progress_message', sa.Text(), nullable=True),
        sa.Column('celery_task_id', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.ForeignKeyConstraint(['template_id'], ['scraping_templates_new.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_scraping_jobs_new_id'), 'scraping_jobs_new', ['id'], unique=False)
    
    # Drop old tables if they exist
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    if 'scraping_jobs' in inspector.get_table_names():
        op.drop_table('scraping_jobs')
    if 'scraping_templates' in inspector.get_table_names():
        op.drop_table('scraping_templates')
        
    # Rename new tables to final names
    op.rename_table('scraping_jobs_new', 'scraping_jobs')
    op.rename_table('scraping_templates_new', 'scraping_templates')


def downgrade():
    op.drop_table('scraping_jobs')
    op.drop_table('scraping_templates')
