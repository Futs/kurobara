from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps
from app.schemas.common import PaginationParams, PaginatedResponse

router = APIRouter()


@router.get("/manga/{manga_id}", response_model=PaginatedResponse[schemas.Chapter])
def read_chapters(
    *,
    db: Session = Depends(deps.get_db),
    manga_id: str,
    pagination: PaginationParams = Depends(),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve chapters for a manga with pagination.
    """
    manga = crud.manga.get(db, id=manga_id)
    if not manga:
        raise HTTPException(status_code=404, detail="Manga not found")
    
    chapters = crud.chapter.get_chapters_by_manga(
        db, manga_id=manga_id, skip=pagination.skip, limit=pagination.limit
    )
    total = crud.chapter.count_by_manga(db, manga_id=manga_id)
    
    return {
        "data": chapters,
        "total": total,
        "skip": pagination.skip,
        "limit": pagination.limit
    }


@router.post("/", response_model=schemas.Chapter)
def create_chapter(
    *,
    db: Session = Depends(deps.get_db),
    chapter_in: schemas.ChapterCreate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Create new chapter.
    """
    manga = crud.manga.get(db, id=chapter_in.manga_id)
    if not manga:
        raise HTTPException(status_code=404, detail="Manga not found")
    
    # Check if chapter already exists
    existing = crud.chapter.get_by_manga_and_number(
        db, manga_id=chapter_in.manga_id, chapter_number=chapter_in.chapter_number
    )
    if existing:
        raise HTTPException(status_code=400, detail="Chapter already exists")
    
    chapter = crud.chapter.create(db, obj_in=chapter_in)
    return chapter


@router.get("/latest-downloaded", response_model=List[dict])
def get_latest_downloaded(
    *,
    db: Session = Depends(deps.get_db),
    limit: int = 10,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get latest downloaded chapters.
    """
    return crud.chapter.get_latest_downloaded(
        db, 
        user_id=current_user.id, 
        limit=limit,
        include_explicit=current_user.show_explicit_on_dashboard
    )


@router.get("/recently-read", response_model=List[dict])
def get_recently_read(
    *,
    db: Session = Depends(deps.get_db),
    limit: int = 10,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get recently read chapters.
    """
    return crud.chapter.get_recently_read(
        db, 
        user_id=current_user.id, 
        limit=limit,
        include_explicit=current_user.show_explicit_on_dashboard
    )


@router.post("/reading-progress", response_model=dict)
def update_reading_progress(
    *,
    db: Session = Depends(deps.get_db),
    manga_id: str = Body(...),
    chapter_number: float = Body(...),
    page_number: int = Body(...),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update reading progress.
    """
    manga = crud.manga.get(db, id=manga_id)
    if not manga:
        raise HTTPException(status_code=404, detail="Manga not found")
    
    chapter = crud.chapter.get_by_manga_and_number(
        db, manga_id=manga_id, chapter_number=chapter_number
    )
    if not chapter:
        raise HTTPException(status_code=404, detail="Chapter not found")
    
    success = crud.chapter.update_reading_progress(
        db, 
        user_id=current_user.id, 
        manga_id=manga_id,
        chapter_number=chapter_number,
        page_number=page_number
    )
    
    if not success:
        raise HTTPException(status_code=404, detail="Manga not in collection")
    
    return {"success": True, "message": "Reading progress updated"}


@router.get("/{chapter_id}", response_model=schemas.Chapter)
def read_chapter(
    *,
    db: Session = Depends(deps.get_db),
    chapter_id: str,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get chapter by ID.
    """
    chapter = crud.chapter.get(db, id=chapter_id)
    if not chapter:
        raise HTTPException(status_code=404, detail="Chapter not found")
    return chapter


@router.put("/{chapter_id}", response_model=schemas.Chapter)
def update_chapter(
    *,
    db: Session = Depends(deps.get_db),
    chapter_id: str,
    chapter_in: schemas.ChapterUpdate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update chapter.
    """
    chapter = crud.chapter.get(db, id=chapter_id)
    if not chapter:
        raise HTTPException(status_code=404, detail="Chapter not found")
    chapter = crud.chapter.update(db, db_obj=chapter, obj_in=chapter_in)
    return chapter


@router.delete("/{chapter_id}", response_model=schemas.Chapter)
def delete_chapter(
    *,
    db: Session = Depends(deps.get_db),
    chapter_id: str,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Delete chapter.
    """
    chapter = crud.chapter.get(db, id=chapter_id)
    if not chapter:
        raise HTTPException(status_code=404, detail="Chapter not found")
    chapter = crud.chapter.remove(db, id=chapter_id)
    return chapter


@router.post("/download/{chapter_id}", response_model=schemas.Chapter)
def download_chapter(
    *,
    db: Session = Depends(deps.get_db),
    chapter_id: str,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Download a chapter.
    """
    chapter = crud.chapter.get(db, id=chapter_id)
    if not chapter:
        raise HTTPException(status_code=404, detail="Chapter not found")
    
    # In a real implementation, this would trigger a download process
    # For this example, we'll just mark it as downloaded
    chapter = crud.chapter.update(
        db, 
        db_obj=chapter, 
        obj_in={"is_downloaded": True, "download_path": f"/downloads/manga/{chapter.manga_id}/chapter_{chapter.chapter_number}"}
    )
    
    return chapter


@router.post("/download-all/{manga_id}", response_model=dict)
def download_all_chapters(
    *,
    db: Session = Depends(deps.get_db),
    manga_id: str,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Download all chapters for a manga.
    """
    manga = crud.manga.get(db, id=manga_id)
    if not manga:
        raise HTTPException(status_code=404, detail="Manga not found")
    
    chapters = crud.chapter.get_chapters_by_manga(db, manga_id=manga_id)
    
    # In a real implementation, this would trigger a download process for all chapters
    # For this example, we'll just mark them all as downloaded
    for chapter in chapters:
        crud.chapter.update(
            db, 
            db_obj=chapter, 
            obj_in={"is_downloaded": True, "download_path": f"/downloads/manga/{manga_id}/chapter_{chapter.chapter_number}"}
        )
    
    return {"success": True, "message": f"Started download of {len(chapters)} chapters"}
