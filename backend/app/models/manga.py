from sqlalchemy import Boolean, Column, String, Integer, ForeignKey, Text, Float, Table, DateTime, func
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from sqlalchemy.orm import relationship
import uuid

from app.models.base import Base

# Association table for many-to-many relationship between users and manga
user_manga = Table(
    "user_manga",
    Base.metadata,
    Column("user_id", UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
    Column("manga_id", UUID(as_uuid=True), ForeignKey("manga.id", ondelete="CASCADE"), primary_key=True),
    Column("added_at", DateTime(timezone=True), server_default=func.now(), nullable=False),
    Column("is_favorite", Boolean, default=False, nullable=False),
    Column("is_monitored", Boolean, default=False, nullable=False),
    Column("monitor_frequency", Integer, default=24, nullable=False),  # Hours
    Column("last_read_chapter", Integer, nullable=True),
    Column("last_read_page", Integer, nullable=True),
    Column("reading_status", String(20), default="plan_to_read", nullable=False),  # plan_to_read, reading, completed, dropped
    Column("updated_at", DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False),
)

class Manga(Base):
    __tablename__ = "manga"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    title = Column(String(255), index=True, nullable=False)
    alternative_titles = Column(JSONB, nullable=True)  # Store alternative titles in different languages
    description = Column(Text, nullable=True)
    cover_image = Column(String(255), nullable=True)  # Path to cover image
    status = Column(String(20), default="ongoing", nullable=False)  # ongoing, completed, hiatus, cancelled
    publication_demographic = Column(String(20), nullable=True)  # shounen, shoujo, seinen, josei
    content_rating = Column(String(20), default="safe", nullable=False)  # safe, suggestive, erotica, pornographic
    is_nsfw = Column(Boolean, default=False, nullable=False)
    is_explicit = Column(Boolean, default=False, nullable=False)
    
    # Metadata
    author = Column(String(100), nullable=True)
    artist = Column(String(100), nullable=True)
    year = Column(Integer, nullable=True)
    tags = Column(ARRAY(String(50)), nullable=True)
    genres = Column(ARRAY(String(50)), nullable=True)
    source_url = Column(String(255), nullable=True)
    source_id = Column(String(50), nullable=True)
    source_name = Column(String(50), nullable=True)
    
    # Relationships
    chapters = relationship("Chapter", back_populates="manga", cascade="all, delete-orphan")
    users = relationship("User", secondary=user_manga, backref="manga_collection")
    bookmarks = relationship("Bookmark", back_populates="manga", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Manga {self.title}>"


class Chapter(Base):
    __tablename__ = "chapters"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    manga_id = Column(UUID(as_uuid=True), ForeignKey("manga.id", ondelete="CASCADE"), nullable=False, index=True)
    chapter_number = Column(Float, nullable=False, index=True)
    title = Column(String(255), nullable=True)
    pages_count = Column(Integer, default=0, nullable=False)
    is_downloaded = Column(Boolean, default=False, nullable=False)
    download_path = Column(String(255), nullable=True)  # Local path to downloaded chapter
    source_url = Column(String(255), nullable=True)
    published_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    manga = relationship("Manga", back_populates="chapters")
    bookmarks = relationship("Bookmark", back_populates="chapter", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Chapter {self.chapter_number} of {self.manga.title if self.manga else self.manga_id}>"


class Bookmark(Base):
    __tablename__ = "bookmarks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    manga_id = Column(UUID(as_uuid=True), ForeignKey("manga.id", ondelete="CASCADE"), nullable=False, index=True)
    chapter_id = Column(UUID(as_uuid=True), ForeignKey("chapters.id", ondelete="CASCADE"), nullable=False, index=True)
    page_number = Column(Integer, nullable=False)
    note = Column(Text, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="bookmarks")
    manga = relationship("Manga", back_populates="bookmarks")
    chapter = relationship("Chapter", back_populates="bookmarks")

    def __repr__(self) -> str:
        return f"<Bookmark on page {self.page_number} of chapter {self.chapter.chapter_number if self.chapter else self.chapter_id}>"