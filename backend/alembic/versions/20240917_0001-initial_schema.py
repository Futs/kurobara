"""Initial schema

Revision ID: 0001
Revises: 
Create Date: 2024-09-17 00:01:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '0001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('email', sa.String(255), unique=True, index=True, nullable=False),
        sa.Column('hashed_password', sa.String(255), nullable=True),
        sa.Column('full_name', sa.String(100), nullable=True),
        sa.Column('is_active', sa.Boolean(), default=True, nullable=False),
        sa.Column('is_superuser', sa.Boolean(), default=False, nullable=False),
        sa.Column('blur_nsfw', sa.Boolean(), default=True, nullable=False),
        sa.Column('show_explicit_on_dashboard', sa.Boolean(), default=False, nullable=False),
        sa.Column('theme', sa.String(20), default='dark', nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
    )
    
    # Create manga table
    op.create_table(
        'manga',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('title', sa.String(255), nullable=False, index=True),
        sa.Column('author', sa.String(100), nullable=False, index=True),
        sa.Column('artist', sa.String(100), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('status', sa.String(20), nullable=False, default='ongoing'),
        sa.Column('year', sa.Integer(), nullable=True),
        sa.Column('genres', postgresql.ARRAY(sa.String(50)), nullable=False, default=[]),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
    )
    
    # Create chapters table
    op.create_table(
        'chapters',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('manga_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('number', sa.Float(), nullable=False),
        sa.Column('title', sa.String(255), nullable=True),
        sa.Column('pages', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['manga_id'], ['manga.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('manga_id', 'number', name='uq_chapter_manga_number')
    )
    
    # Create user_manga table (for tracking reading status)
    op.create_table(
        'user_manga',
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('manga_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('reading_status', sa.String(20), nullable=False, default='plan_to_read'),
        sa.Column('is_favorite', sa.Boolean(), nullable=False, default=False),
        sa.Column('last_read_chapter', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('last_read_page', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['manga_id'], ['manga.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['last_read_chapter'], ['chapters.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('user_id', 'manga_id')
    )
    
    # Create bookmarks table
    op.create_table(
        'bookmarks',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('manga_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('chapter_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('page_number', sa.Integer(), nullable=False),
        sa.Column('note', sa.String(500), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['manga_id'], ['manga.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['chapter_id'], ['chapters.id'], ondelete='CASCADE'),
    )
    
    # Create indexes
    op.create_index('ix_manga_title', 'manga', ['title'])
    op.create_index('ix_manga_author', 'manga', ['author'])
    op.create_index('ix_chapters_manga_id', 'chapters', ['manga_id'])
    op.create_index('ix_chapters_number', 'chapters', ['number'])
    op.create_index('ix_bookmarks_user_id', 'bookmarks', ['user_id'])
    op.create_index('ix_bookmarks_manga_id', 'bookmarks', ['manga_id'])
    op.create_index('ix_bookmarks_chapter_id', 'bookmarks', ['chapter_id'])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('bookmarks')
    op.drop_table('user_manga')
    op.drop_table('chapters')
    op.drop_table('manga')
    op.drop_table('users')