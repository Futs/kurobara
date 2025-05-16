from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from uuid import UUID

from app.crud.base import CRUDBase
from app.models.manga import Bookmark
from app.schemas.manga import BookmarkCreate, BookmarkUpdate

class CRUDBookmark(CRUDBase[Bookmark, BookmarkCreate, BookmarkUpdate]):
    def create_bookmark(
        self, db: Session, *, user_id: UUID, obj_in: BookmarkCreate
    ) -> Bookmark:
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
            raise
    
    def get_multi_by_user(
        self, db: Session, *, user_id: UUID, skip: int = 0, limit: int = 100
    ) -> List[Bookmark]:
        return db.query(Bookmark).filter(
            Bookmark.user_id == user_id
        ).offset(skip).limit(limit).all()
        
    def get_by_user_and_manga(
        self, db: Session, *, user_id: UUID, manga_id: UUID
    ) -> List[Bookmark]:
        return db.query(Bookmark).filter(
            Bookmark.user_id == user_id,
            Bookmark.manga_id == manga_id
        ).all()
        
    def get_by_user_and_chapter(
        self, db: Session, *, user_id: UUID, chapter_id: UUID
    ) -> List[Bookmark]:
        return db.query(Bookmark).filter(
            Bookmark.user_id == user_id,
            Bookmark.chapter_id == chapter_id
        ).all()
