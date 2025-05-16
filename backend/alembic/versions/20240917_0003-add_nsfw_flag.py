"""Add NSFW flag

Revision ID: 0003
Revises: 0002
Create Date: 2024-09-17 00:03:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0003'
down_revision: Union[str, None] = '0002'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add NSFW flag to manga table
    op.add_column('manga', sa.Column('is_nsfw', sa.Boolean(), nullable=False, server_default='false'))
    
    # Add NSFW flag to chapters table
    op.add_column('chapters', sa.Column('is_nsfw', sa.Boolean(), nullable=False, server_default='false'))
    
    # Create index for NSFW filtering
    op.create_index('ix_manga_is_nsfw', 'manga', ['is_nsfw'])


def downgrade() -> None:
    """Downgrade schema."""
    # Drop index
    op.drop_index('ix_manga_is_nsfw', table_name='manga')
    
    # Drop columns
    op.drop_column('chapters', 'is_nsfw')
    op.drop_column('manga', 'is_nsfw')