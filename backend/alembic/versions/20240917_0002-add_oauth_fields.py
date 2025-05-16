"""Add OAuth fields

Revision ID: 0002
Revises: 0001
Create Date: 2024-09-17 00:02:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0002'
down_revision: Union[str, None] = '0001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add OAuth fields to users table
    op.add_column('users', sa.Column('oauth_provider', sa.String(20), nullable=True))
    op.add_column('users', sa.Column('oauth_id', sa.String(255), nullable=True))
    
    # Add two-factor authentication fields
    op.add_column('users', sa.Column('two_factor_enabled', sa.Boolean(), nullable=False, server_default='false'))
    op.add_column('users', sa.Column('two_factor_secret', sa.String(255), nullable=True))
    
    # Create unique constraint for oauth_provider and oauth_id
    op.create_unique_constraint('uq_users_oauth', 'users', ['oauth_provider', 'oauth_id'])
    
    # Create index for oauth lookups
    op.create_index('ix_users_oauth', 'users', ['oauth_provider', 'oauth_id'])


def downgrade() -> None:
    """Downgrade schema."""
    # Drop index and constraint
    op.drop_index('ix_users_oauth', table_name='users')
    op.drop_constraint('uq_users_oauth', 'users', type_='unique')
    
    # Drop columns
    op.drop_column('users', 'two_factor_secret')
    op.drop_column('users', 'two_factor_enabled')
    op.drop_column('users', 'oauth_id')
    op.drop_column('users', 'oauth_provider')