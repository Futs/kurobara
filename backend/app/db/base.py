"""
Import all models here to ensure SQLAlchemy and Alembic can discover them.
This file is imported by Alembic migrations and app initialization.
"""

from app.db.database import Base  # noqa
from app.models.user import User  # noqa
from app.models.manga import Manga, Chapter, Bookmark  # noqa