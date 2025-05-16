from fastapi import APIRouter, Depends
from app.core.limiter import default_rate_limit
from app.core.config import settings

from app.api.api_v1.endpoints import login, users, manga, chapters, bookmarks

api_router = APIRouter()
api_router.include_router(login.router, tags=["login"])

# Apply default rate limiting to all other endpoints if enabled
if hasattr(settings, 'RATE_LIMITING_ENABLED') and settings.RATE_LIMITING_ENABLED:
    api_router.include_router(
        users.router, 
        prefix="/users", 
        tags=["users"], 
        dependencies=[Depends(default_rate_limit())]
    )
    api_router.include_router(
        manga.router, 
        prefix="/manga", 
        tags=["manga"], 
        dependencies=[Depends(default_rate_limit())]
    )
    api_router.include_router(
        chapters.router, 
        prefix="/chapters", 
        tags=["chapters"], 
        dependencies=[Depends(default_rate_limit())]
    )
    api_router.include_router(
        bookmarks.router, 
        prefix="/bookmarks", 
        tags=["bookmarks"], 
        dependencies=[Depends(default_rate_limit())]
    )
else:
    # Include routers without rate limiting if disabled
    api_router.include_router(users.router, prefix="/users", tags=["users"])
    api_router.include_router(manga.router, prefix="/manga", tags=["manga"])
    api_router.include_router(chapters.router, prefix="/chapters", tags=["chapters"])
    api_router.include_router(bookmarks.router, prefix="/bookmarks", tags=["bookmarks"])
