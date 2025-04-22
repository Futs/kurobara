import logging
from typing import List, Dict, Any
from sqlalchemy.orm import Session

from app import crud, schemas
from app.core.config import settings
from app.db import base  # noqa: F401

# Import all the models to ensure they are registered with SQLAlchemy
from app.models.user import User  # noqa
from app.models.manga import Manga, Chapter, Bookmark  # noqa

logger = logging.getLogger(__name__)


def init_db(db: Session) -> None:
    """Initialize database with default data if empty."""
    _create_initial_superuser(db)
    _create_sample_manga_data(db)


def _create_initial_superuser(db: Session) -> None:
    """Create the initial superuser if it doesn't exist."""
    user = crud.user.get_by_email(db, email=settings.FIRST_SUPERUSER)
    if not user:
        try:
            user_in = schemas.UserCreate(
                email=settings.FIRST_SUPERUSER,
                password=settings.FIRST_SUPERUSER_PASSWORD,
                is_superuser=True,
                full_name="Initial Super User",
            )
            user = crud.user.create(db, obj_in=user_in)
            logger.info(f"Superuser {settings.FIRST_SUPERUSER} created")
        except Exception as e:
            logger.error(f"Failed to create superuser: {e}")
    else:
        logger.info(f"Superuser {settings.FIRST_SUPERUSER} already exists")


def _create_sample_manga_data(db: Session) -> None:
    """Create sample manga data if the database is empty."""
    manga_count = db.query(Manga).count()
    if manga_count > 0:
        logger.info("Database already contains manga data")
        return
    
    sample_mangas = [
        {
            "title": "One Piece",
            "alternative_titles": {"ja": "ワンピース", "en": "One Piece"},
            "description": "The story follows the adventures of Monkey D. Luffy, a boy whose body gained the properties of rubber after unintentionally eating a Devil Fruit.",
            "status": "ongoing",
            "publication_demographic": "shounen",
            "content_rating": "safe",
            "is_nsfw": False,
            "is_explicit": False,
            "author": "Eiichiro Oda",
            "artist": "Eiichiro Oda",
            "year": 1997,
            "tags": ["adventure", "fantasy", "pirates"],
            "genres": ["Action", "Adventure", "Comedy", "Fantasy"],
            "source_name": "Sample"
        },
        {
            "title": "Naruto",
            "alternative_titles": {"ja": "ナルト", "en": "Naruto"},
            "description": "It tells the story of Naruto Uzumaki, a young ninja who seeks recognition from his peers and dreams of becoming the Hokage, the leader of his village.",
            "status": "completed",
            "publication_demographic": "shounen",
            "content_rating": "safe",
            "is_nsfw": False,
            "is_explicit": False,
            "author": "Masashi Kishimoto",
            "artist": "Masashi Kishimoto",
            "year": 1999,
            "tags": ["ninja", "fantasy", "martial arts"],
            "genres": ["Action", "Adventure", "Fantasy"],
            "source_name": "Sample"
        }
    ]
    
    for manga_data in sample_mangas:
        try:
            manga_in = schemas.MangaCreate(**manga_data)
            manga = crud.manga.create(db, obj_in=manga_in)
            logger.info(f"Sample manga '{manga.title}' created")
            
            # Add 5 sample chapters for each manga
            _create_sample_chapters(db, manga.id)
        except Exception as e:
            logger.error(f"Failed to create manga '{manga_data['title']}': {e}")


def _create_sample_chapters(db: Session, manga_id: int) -> None:
    """Create sample chapters for a manga."""
    try:
        for i in range(1, 6):
            chapter_in = schemas.ChapterCreate(
                manga_id=manga_id,
                chapter_number=float(i),
                title=f"Chapter {i}",
                pages_count=20,
            )
            crud.chapter.create(db, obj_in=chapter_in)
        
        manga = db.query(Manga).filter(Manga.id == manga_id).first()
        if manga:
            logger.info(f"Added 5 sample chapters to '{manga.title}'")
    except Exception as e:
        logger.error(f"Failed to create chapters for manga_id {manga_id}: {e}")