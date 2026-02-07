"""Add contact pool and VCF batch tables

Revision ID: b7f8d92e1234
Revises: a5e9c37a230a
Create Date: 2026-02-06 20:55:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'b7f8d92e1234'
down_revision: Union[str, None] = 'a5e9c37a230a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add new columns to users table
    op.add_column('users', sa.Column('last_activity_at', sa.DateTime(), nullable=True))
    op.add_column('users', sa.Column('tutorial_completed', sa.Boolean(), server_default='false', nullable=True))
    op.add_column('users', sa.Column('notification_token', sa.String(), nullable=True))
    
    # Create vcf_batches table first (referenced by contact_pool and agent_progress)
    op.create_table('vcf_batches',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('agent_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('file_path', sa.String(), nullable=True),
        sa.Column('file_name', sa.String(), nullable=True),
        sa.Column('contact_count', sa.Integer(), server_default='0', nullable=True),
        sa.Column('prefix', sa.String(), server_default='LEG', nullable=True),
        sa.Column('start_serial', sa.Integer(), server_default='1', nullable=True),
        sa.Column('contacts_per_serial', sa.Integer(), server_default='25', nullable=True),
        sa.Column('status', sa.String(), server_default='PENDING', nullable=True),
        sa.Column('assigned_at', sa.DateTime(), nullable=True),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('total_reported', sa.Integer(), server_default='0', nullable=True),
        sa.ForeignKeyConstraint(['agent_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_vcf_batches_tenant_id'), 'vcf_batches', ['tenant_id'], unique=False)
    op.create_index(op.f('ix_vcf_batches_agent_id'), 'vcf_batches', ['agent_id'], unique=False)
    op.create_index(op.f('ix_vcf_batches_status'), 'vcf_batches', ['status'], unique=False)
    
    # Create contact_pool table
    op.create_table('contact_pool',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('phone', sa.String(), nullable=False),
        sa.Column('source_file', sa.String(), nullable=True),
        sa.Column('uploaded_at', sa.DateTime(), nullable=True),
        sa.Column('vcf_batch_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('is_assigned', sa.Boolean(), server_default='false', nullable=True),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ),
        sa.ForeignKeyConstraint(['vcf_batch_id'], ['vcf_batches.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_contact_pool_tenant_id'), 'contact_pool', ['tenant_id'], unique=False)
    op.create_index(op.f('ix_contact_pool_is_assigned'), 'contact_pool', ['is_assigned'], unique=False)
    op.create_index(op.f('ix_contact_pool_phone'), 'contact_pool', ['phone'], unique=False)
    
    # Create agent_progress table
    op.create_table('agent_progress',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('agent_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('vcf_batch_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('date', sa.Date(), nullable=True),
        sa.Column('morning_count', sa.Integer(), server_default='0', nullable=True),
        sa.Column('evening_count', sa.Integer(), server_default='0', nullable=True),
        sa.Column('morning_reported_at', sa.DateTime(), nullable=True),
        sa.Column('evening_reported_at', sa.DateTime(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['agent_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['vcf_batch_id'], ['vcf_batches.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_agent_progress_agent_id'), 'agent_progress', ['agent_id'], unique=False)
    op.create_index(op.f('ix_agent_progress_date'), 'agent_progress', ['date'], unique=False)


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_index(op.f('ix_agent_progress_date'), table_name='agent_progress')
    op.drop_index(op.f('ix_agent_progress_agent_id'), table_name='agent_progress')
    op.drop_table('agent_progress')
    
    op.drop_index(op.f('ix_contact_pool_phone'), table_name='contact_pool')
    op.drop_index(op.f('ix_contact_pool_is_assigned'), table_name='contact_pool')
    op.drop_index(op.f('ix_contact_pool_tenant_id'), table_name='contact_pool')
    op.drop_table('contact_pool')
    
    op.drop_index(op.f('ix_vcf_batches_status'), table_name='vcf_batches')
    op.drop_index(op.f('ix_vcf_batches_agent_id'), table_name='vcf_batches')
    op.drop_index(op.f('ix_vcf_batches_tenant_id'), table_name='vcf_batches')
    op.drop_table('vcf_batches')
    
    # Remove columns from users
    op.drop_column('users', 'notification_token')
    op.drop_column('users', 'tutorial_completed')
    op.drop_column('users', 'last_activity_at')
