from typing import Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Body
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps
from app.schemas.common import PaginationParams, PaginatedResponse
from app.core.limiter import search_rate_limit

router = APIRouter()


@router.get("/", response_model=PaginatedResponse[schemas.Manga])
def read_manga(
    db: Session = Depends(deps.get_db),
    pagination: PaginationParams = Depends(),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve manga with pagination.
    """
    manga = crud.manga.get_multi(db, skip=pagination.skip, limit=pagination.limit)
    total = crud.manga.count(db)
    return {
        "data": manga,
        "total": total,
        "skip": pagination.skip,
        "limit": pagination.limit
    }


@router.post("/", response_model=schemas.Manga)
def create_manga(
    *,
    db: Session = Depends(deps.get_db),
    manga_in: schemas.MangaCreate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Create new manga.
    """
    manga = crud.manga.create(db, obj_in=manga_in)
    return manga


@router.get("/search", response_model=List[schemas.Manga])
async def search_manga(
    *,
    db: Session = Depends(deps.get_db),
    query: str,
    current_user: models.User = Depends(deps.get_current_active_user),
    rate_limiter: None = Depends(search_rate_limit()),
) -> Any:
    """
    Search for manga by title.
    """
    return crud.manga.search(db, query=query)


@router.get("/collection", response_model=List[schemas.Manga])
def get_user_collection(
    *,
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get manga in user's collection.
    """
    manga = crud.manga.get_user_manga(
        db, user_id=current_user.id, skip=skip, limit=limit
    )
    return manga


@router.post("/collection/{manga_id}", response_model=dict)
def add_to_collection(
    *,
    db: Session = Depends(deps.get_db),
    manga_id: str,
    is_favorite: bool = Body(False),
    is_monitored: bool = Body(False),
    monitor_frequency: int = Body(24),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Add manga to user's collection.
    """
    manga = crud.manga.get(db, id=manga_id)
    if not manga:
        raise HTTPException(status_code=404, detail="Manga not found")
    
    success = crud.manga.add_to_user_collection(
        db, 
        user_id=current_user.id, 
        manga_id=manga_id,
        is_favorite=is_favorite,
        is_monitored=is_monitored,
        monitor_frequency=monitor_frequency
    )
    
    if not success:
        return {"success": False, "message": "Manga already in collection"}
    
    return {"success": True, "message": "Manga added to collection"}


@router.put("/collection/{manga_id}", response_model=dict)
def update_collection_manga(
    *,
    db: Session = Depends(deps.get_db),
    manga_id: str,
    is_favorite: Optional[bool] = Body(None),
    is_monitored: Optional[bool] = Body(None),
    monitor_frequency: Optional[int] = Body(None),
    reading_status: Optional[str] = Body(None),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update manga in user's collection.
    """
    manga = crud.manga.get(db, id=manga_id)
    if not manga:
        raise HTTPException(status_code=404, detail="Manga not found")
    
    success = crud.manga.update_user_manga(
        db, 
        user_id=current_user.id, 
        manga_id=manga_id,
        is_favorite=is_favorite,
        is_monitored=is_monitored,
        monitor_frequency=monitor_frequency,
        reading_status=reading_status
    )
    
    if not success:
        raise HTTPException(status_code=404, detail="Manga not in collection")
    
    return {"success": True, "message": "Manga updated in collection"}


@router.delete("/collection/{manga_id}", response_model=dict)
def remove_from_collection(
    *,
    db: Session = Depends(deps.get_db),
    manga_id: str,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Remove manga from user's collection.
    """
    success = crud.manga.remove_from_user_collection(
        db, user_id=current_user.id, manga_id=manga_id
    )
    
    if not success:
        raise HTTPException(status_code=404, detail="Manga not in collection")
    
    return {"success": True, "message": "Manga removed from collection"}


@router.get("/latest-added", response_model=List[dict])
def get_latest_added(
    *,
    db: Session = Depends(deps.get_db),
    limit: int = 10,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get latest manga added to user's collection.
    """
    return crud.manga.get_latest_added(
        db, 
        user_id=current_user.id, 
        limit=limit,
        include_explicit=current_user.show_explicit_on_dashboard
    )


@router.get("/{manga_id}", response_model=schemas.Manga)
def read_manga(
    *,
    db: Session = Depends(deps.get_db),
    manga_id: str,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get manga by ID.
    """
    manga = crud.manga.get(db, id=manga_id)
    if not manga:
        raise HTTPException(status_code=404, detail="Manga not found")
    return manga


@router.put("/{manga_id}", response_model=schemas.Manga)
def update_manga(
    *,
    db: Session = Depends(deps.get_db),
    manga_id: str,
    manga_in: schemas.MangaUpdate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update manga.
    """
    manga = crud.manga.get(db, id=manga_id)
    if not manga:
        raise HTTPException(status_code=404, detail="Manga not found")
    manga = crud.manga.update(db, db_obj=manga, obj_in=manga_in)
    return manga


@router.delete("/{manga_id}", response_model=schemas.Manga)
def delete_manga(
    *,
    db: Session = Depends(deps.get_db),
    manga_id: str,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Delete manga.
    """
    manga = crud.manga.get(db, id=manga_id)
    if not manga:
        raise HTTPException(status_code=404, detail="Manga not found")
    manga = crud.manga.remove(db, id=manga_id)
    return manga
