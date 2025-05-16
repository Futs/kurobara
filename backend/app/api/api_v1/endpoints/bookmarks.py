from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps

router = APIRouter()


@router.get("/", response_model=List[schemas.Bookmark])
def read_bookmarks(
    *,
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve bookmarks for the current user.
    """
    # Use the CRUD method instead of direct query
    bookmarks = crud.bookmark.get_multi_by_user(
        db, user_id=current_user.id, skip=skip, limit=limit
    )
    return bookmarks


@router.post("/", response_model=schemas.Bookmark)
def create_bookmark(
    *,
    db: Session = Depends(deps.get_db),
    bookmark_in: schemas.BookmarkCreate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Create new bookmark.
    """
    # Check if manga exists
    manga = crud.manga.get(db, id=bookmark_in.manga_id)
    if not manga:
        raise HTTPException(status_code=404, detail="Manga not found")
    
    # Check if chapter exists
    chapter = crud.chapter.get(db, id=bookmark_in.chapter_id)
    if not chapter:
        raise HTTPException(status_code=404, detail="Chapter not found")
    
    # Check if chapter belongs to manga
    if str(chapter.manga_id) != str(bookmark_in.manga_id):
        raise HTTPException(status_code=400, detail="Chapter does not belong to manga")
    
    bookmark = crud.bookmark.create_bookmark(db, user_id=current_user.id, obj_in=bookmark_in)
    return bookmark


@router.get("/manga/{manga_id}", response_model=List[schemas.Bookmark])
def read_manga_bookmarks(
    *,
    db: Session = Depends(deps.get_db),
    manga_id: str,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve bookmarks for a manga.
    """
    manga = crud.manga.get(db, id=manga_id)
    if not manga:
        raise HTTPException(status_code=404, detail="Manga not found")
    
    bookmarks = crud.bookmark.get_by_user_and_manga(
        db, user_id=current_user.id, manga_id=manga_id
    )
    return bookmarks


@router.get("/chapter/{chapter_id}", response_model=List[schemas.Bookmark])
def read_chapter_bookmarks(
    *,
    db: Session = Depends(deps.get_db),
    chapter_id: str,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve bookmarks for a chapter.
    """
    chapter = crud.chapter.get(db, id=chapter_id)
    if not chapter:
        raise HTTPException(status_code=404, detail="Chapter not found")
    
    bookmarks = crud.bookmark.get_by_user_and_chapter(
        db, user_id=current_user.id, chapter_id=chapter_id
    )
    return bookmarks


@router.get("/{bookmark_id}", response_model=schemas.Bookmark)
def read_bookmark(
    *,
    db: Session = Depends(deps.get_db),
    bookmark_id: str,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get bookmark by ID.
    """
    bookmark = crud.bookmark.get(db, id=bookmark_id)
    if not bookmark:
        raise HTTPException(status_code=404, detail="Bookmark not found")
    
    # Check if bookmark belongs to user
    if str(bookmark.user_id) != str(current_user.id):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    return bookmark


@router.put("/{bookmark_id}", response_model=schemas.Bookmark)
def update_bookmark(
    *,
    db: Session = Depends(deps.get_db),
    bookmark_id: str,
    bookmark_in: schemas.BookmarkUpdate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update bookmark.
    """
    bookmark = crud.bookmark.get(db, id=bookmark_id)
    if not bookmark:
        raise HTTPException(status_code=404, detail="Bookmark not found")
    
    # Check if bookmark belongs to user
    if str(bookmark.user_id) != str(current_user.id):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    bookmark = crud.bookmark.update(db, db_obj=bookmark, obj_in=bookmark_in)
    return bookmark


@router.delete("/{bookmark_id}", response_model=schemas.Bookmark)
def delete_bookmark(
    *,
    db: Session = Depends(deps.get_db),
    bookmark_id: str,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Delete bookmark.
    """
    bookmark = crud.bookmark.get(db, id=bookmark_id)
    if not bookmark:
        raise HTTPException(status_code=404, detail="Bookmark not found")
    
    # Check if bookmark belongs to user
    if str(bookmark.user_id) != str(current_user.id):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    bookmark = crud.bookmark.remove(db, id=bookmark_id)
    return bookmark
