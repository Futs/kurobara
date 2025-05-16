from typing import Any, Dict, List, Optional, Union, Tuple
from uuid import UUID

from sqlalchemy import and_, or_, func, desc, text
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import SQLAlchemyError

from app.crud.base import CRUDBase
from app.models.manga import Manga, Chapter, Bookmark, user_manga
from app.schemas.manga import MangaCreate, MangaUpdate, ChapterCreate, ChapterUpdate, BookmarkCreate, BookmarkUpdate


class CRUDManga(CRUDBase[Manga, MangaCreate, MangaUpdate]):
    def search(
        self, db: Session, *, query: str, include_nsfw: bool = False, include_explicit: bool = False, 
        skip: int = 0, limit: int = 100
    ) -> List[Tuple[Manga, float]]:
        """
        Search for manga with a text query and return results with accuracy scores.
        """
        if not query:
            return []
            
        # Convert query to lowercase for case-insensitive search
        search_query = f"%{query.lower()}%"
        
        # Base query with filters for NSFW/explicit content
        base_query = db.query(Manga)
        
        if not include_nsfw:
            base_query = base_query.filter(Manga.is_nsfw == False)
        
        if not include_explicit:
            base_query = base_query.filter(Manga.is_explicit == False)
        
        # Search in title, alternative titles, description, author, artist
        results = base_query.filter(
            or_(
                func.lower(Manga.title).like(search_query),
                Manga.alternative_titles.cast(str).like(search_query),
                func.lower(Manga.description).like(search_query),
                func.lower(Manga.author).like(search_query),
                func.lower(Manga.artist).like(search_query)
            )
        ).offset(skip).limit(limit).all()
        
        # Calculate accuracy scores with improved algorithm
        query_lower = query.lower()
        scored_results = []
        for manga in results:
            # Initialize score
            accuracy = 0.0
            
            # Title matches get highest priority
            if manga.title:
                if query_lower == manga.title.lower():
                    accuracy = max(accuracy, 1.0)  # Exact match
                elif query_lower in manga.title.lower():
                    accuracy = max(accuracy, 0.9)  # Partial match
            
            # Author/artist matches
            if manga.author and query_lower in manga.author.lower():
                accuracy = max(accuracy, 0.7)
            if manga.artist and query_lower in manga.artist.lower():
                accuracy = max(accuracy, 0.7)
            
            # Description matches
            if manga.description and query_lower in manga.description.lower():
                accuracy = max(accuracy, 0.5)
            
            # Alternative titles
            if manga.alternative_titles:
                for alt_title in manga.alternative_titles:
                    if alt_title and query_lower in alt_title.lower():
                        accuracy = max(accuracy, 0.6)
                        break
            
            scored_results.append((manga, accuracy))
            
        # Sort by accuracy score (highest first)
        return sorted(scored_results, key=lambda x: x[1], reverse=True)

    def get_user_manga(
        self, db: Session, *, user_id: UUID, skip: int = 0, limit: int = 100
    ) -> List[Manga]:
        """Get all manga in a user's collection"""
        try:
            return db.query(Manga).join(
                user_manga, Manga.id == user_manga.c.manga_id
            ).filter(
                user_manga.c.user_id == user_id
            ).offset(skip).limit(limit).all()
        except SQLAlchemyError:
            db.rollback()
            return []
    
    def get_latest_added(
        self, db: Session, *, user_id: UUID, limit: int = 10, include_explicit: bool = False
    ) -> List[Dict[str, Any]]:
        """Get the latest manga added to a user's collection"""
        try:
            query = db.query(
                Manga, 
                user_manga.c.added_at
            ).join(
                user_manga, Manga.id == user_manga.c.manga_id
            ).filter(
                user_manga.c.user_id == user_id
            )
            
            if not include_explicit:
                query = query.filter(Manga.is_explicit == False)
                
            results = query.order_by(
                desc(user_manga.c.added_at)
            ).limit(limit).all()
            
            return [
                {
                    "manga": manga,
                    "added_at": added_at
                } for manga, added_at in results
            ]
        except SQLAlchemyError:
            db.rollback()
            return []
    
    def add_to_user_collection(
        self, db: Session, *, user_id: UUID, manga_id: UUID, 
        is_favorite: bool = False, is_monitored: bool = False,
        monitor_frequency: int = 24
    ) -> bool:
        """Add a manga to a user's collection"""
        try:
            # Check if already in collection
            existing = db.query(user_manga).filter(
                user_manga.c.user_id == user_id,
                user_manga.c.manga_id == manga_id
            ).first()
            
            if existing:
                return False
            
            # Add to collection
            db.execute(
                user_manga.insert().values(
                    user_id=user_id,
                    manga_id=manga_id,
                    is_favorite=is_favorite,
                    is_monitored=is_monitored,
                    monitor_frequency=monitor_frequency
                )
            )
            db.commit()
            return True
        except SQLAlchemyError:
            db.rollback()
            return False
    
    def update_user_manga(
        self, db: Session, *, user_id: UUID, manga_id: UUID,
        is_favorite: Optional[bool] = None, is_monitored: Optional[bool] = None,
        monitor_frequency: Optional[int] = None, reading_status: Optional[str] = None
    ) -> bool:
        """Update a manga in a user's collection"""
        try:
            # Check if in collection
            existing = db.query(user_manga).filter(
                user_manga.c.user_id == user_id,
                user_manga.c.manga_id == manga_id
            ).first()
            
            if not existing:
                return False
            
            # Build update values
            values = {}
            if is_favorite is not None:
                values["is_favorite"] = is_favorite
            if is_monitored is not None:
                values["is_monitored"] = is_monitored
            if monitor_frequency is not None:
                values["monitor_frequency"] = monitor_frequency
            if reading_status is not None:
                values["reading_status"] = reading_status
                
            if not values:
                return True  # Nothing to update
            
            # Add updated_at timestamp
            values["updated_at"] = func.now()
            
            # Update collection
            db.execute(
                user_manga.update().where(
                    and_(
                        user_manga.c.user_id == user_id,
                        user_manga.c.manga_id == manga_id
                    )
                ).values(**values)
            )
            db.commit()
            return True
        except SQLAlchemyError:
            db.rollback()
            return False
    
    def remove_from_user_collection(
        self, db: Session, *, user_id: UUID, manga_id: UUID
    ) -> bool:
        """Remove a manga from a user's collection"""
        try:
            result = db.execute(
                user_manga.delete().where(
                    and_(
                        user_manga.c.user_id == user_id,
                        user_manga.c.manga_id == manga_id
                    )
                )
            )
            db.commit()
            return result.rowcount > 0
        except SQLAlchemyError:
            db.rollback()
            return False
    
    def get_monitored_manga(
        self, db: Session, *, user_id: Optional[UUID] = None
    ) -> List[Dict[str, Any]]:
        """Get all monitored manga, optionally filtered by user"""
        try:
            query = db.query(
                Manga,
                user_manga.c.user_id,
                user_manga.c.monitor_frequency
            ).join(
                user_manga, Manga.id == user_manga.c.manga_id
            ).filter(
                user_manga.c.is_monitored == True
            )
            
            if user_id:
                query = query.filter(user_manga.c.user_id == user_id)
                
            results = query.all()
            
            return [
                {
                    "manga": manga,
                    "user_id": uid,
                    "monitor_frequency": frequency
                } for manga, uid, frequency in results
            ]
        except SQLAlchemyError:
            db.rollback()
            return []


class CRUDChapter(CRUDBase[Chapter, ChapterCreate, ChapterUpdate]):
    def get_by_manga_and_number(
        self, db: Session, *, manga_id: UUID, chapter_number: float
    ) -> Optional[Chapter]:
        """Get a chapter by manga ID and chapter number"""
        try:
            return db.query(Chapter).filter(
                Chapter.manga_id == manga_id,
                Chapter.chapter_number == chapter_number
            ).first()
        except SQLAlchemyError:
            db.rollback()
            return None
    
    def get_chapters_by_manga(
        self, db: Session, *, manga_id: UUID, skip: int = 0, limit: int = 100
    ) -> List[Chapter]:
        """Get all chapters for a manga"""
        try:
            return db.query(Chapter).filter(
                Chapter.manga_id == manga_id
            ).order_by(Chapter.chapter_number).offset(skip).limit(limit).all()
        except SQLAlchemyError:
            db.rollback()
            return []
    
    def count_by_manga(self, db: Session, *, manga_id: UUID) -> int:
        """Count chapters for a specific manga"""
        try:
            return db.query(Chapter).filter(Chapter.manga_id == manga_id).count()
        except SQLAlchemyError:
            db.rollback()
            return 0
    
    def get_latest_downloaded(
        self, db: Session, *, user_id: UUID, limit: int = 10, include_explicit: bool = False
    ) -> List[Dict[str, Any]]:
        """Get the latest downloaded chapters for a user"""
        try:
            query = db.query(
                Chapter, Manga
            ).join(
                Manga, Chapter.manga_id == Manga.id
            ).join(
                user_manga, Manga.id == user_manga.c.manga_id
            ).filter(
                user_manga.c.user_id == user_id,
                Chapter.is_downloaded == True
            )
            
            if not include_explicit:
                query = query.filter(Manga.is_explicit == False)
                
            results = query.order_by(
                desc(Chapter.updated_at)
            ).limit(limit).all()
            
            return [
                {
                    "chapter": chapter,
                    "manga": manga
                } for chapter, manga in results
            ]
        except SQLAlchemyError:
            db.rollback()
            return []
    
    def get_recently_read(
        self, db: Session, *, user_id: UUID, limit: int = 10, include_explicit: bool = False
    ) -> List[Dict[str, Any]]:
        """Get recently read chapters for a user"""
        try:
            query = db.query(
                Chapter, Manga, user_manga.c.last_read_page
            ).join(
                Manga, Chapter.manga_id == Manga.id
            ).join(
                user_manga, Manga.id == user_manga.c.manga_id
            ).filter(
                user_manga.c.user_id == user_id,
                user_manga.c.last_read_chapter == Chapter.chapter_number
            )
            
            if not include_explicit:
                query = query.filter(Manga.is_explicit == False)
                
            results = query.order_by(
                desc(user_manga.c.updated_at)
            ).limit(limit).all()
            
            return [
                {
                    "chapter": chapter,
                    "manga": manga,
                    "last_page": last_page
                } for chapter, manga, last_page in results
            ]
        except SQLAlchemyError:
            db.rollback()
            return []
    
    def update_reading_progress(
        self, db: Session, *, user_id: UUID, manga_id: UUID, 
        chapter_number: float, page_number: int
    ) -> bool:
        """Update a user's reading progress for a manga"""
        try:
            result = db.execute(
                user_manga.update().where(
                    and_(
                        user_manga.c.user_id == user_id,
                        user_manga.c.manga_id == manga_id
                    )
                ).values(
                    last_read_chapter=chapter_number,
                    last_read_page=page_number,
                    updated_at=func.now()
                )
            )
            db.commit()
            return result.rowcount > 0
        except SQLAlchemyError:
            db.rollback()
            return False


class CRUDBookmark(CRUDBase[Bookmark, BookmarkCreate, BookmarkUpdate]):
    def get_by_user_and_chapter(
        self, db: Session, *, user_id: UUID, chapter_id: UUID
    ) -> List[Bookmark]:
        """Get all bookmarks for a user in a chapter"""
        try:
            return db.query(Bookmark).filter(
                Bookmark.user_id == user_id,
                Bookmark.chapter_id == chapter_id
            ).all()
        except SQLAlchemyError:
            db.rollback()
            return []
    
    def get_by_user_and_manga(
        self, db: Session, *, user_id: UUID, manga_id: UUID
    ) -> List[Bookmark]:
        """Get all bookmarks for a user in a manga"""
        try:
            return db.query(Bookmark).filter(
                Bookmark.user_id == user_id,
                Bookmark.manga_id == manga_id
            ).all()
        except SQLAlchemyError:
            db.rollback()
            return []
    
    def create_bookmark(
        self, db: Session, *, user_id: UUID, obj_in: BookmarkCreate
    ) -> Optional[Bookmark]:
        """Create a bookmark for a user"""
        try:
            db_obj = Bookmark(
                user_id=user_id,
                manga_id=obj_in.manga_id,
                chapter_id=obj_in.chapter_id,
                page_number=obj_in.page_number,
                note=obj_in.note
            )
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
            return db_obj
        except SQLAlchemyError:
            db.rollback()
            return None


manga = CRUDManga(Manga)
chapter = CRUDChapter(Chapter)
bookmark = CRUDBookmark(Bookmark)
