from sqlalchemy import Boolean, Column, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from app.models.base import Base


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=True)  # Nullable for OAuth users
    full_name = Column(String(100), index=True, nullable=True)
    is_active = Column(Boolean(), default=True, nullable=False)
    is_superuser = Column(Boolean(), default=False, nullable=False)
    
    # OAuth related fields
    oauth_provider = Column(String(50), nullable=True)  # "google", "email", etc.
    oauth_id = Column(String(255), nullable=True)
    
    # 2FA related fields
    two_factor_secret = Column(String(255), nullable=True)
    two_factor_enabled = Column(Boolean(), default=False, nullable=False)
    
    # User preferences
    blur_nsfw = Column(Boolean(), default=True, nullable=False)
    show_explicit_on_dashboard = Column(Boolean(), default=False, nullable=False)
    theme = Column(String(20), default="dark", nullable=False)  # "dark" or "light"
    
    # Relationship to manga collection is defined via backref in manga.py
    
    # Add relationship to bookmarks
    bookmarks = relationship("Bookmark", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<User {self.email}>"