from fastapi import APIRouter

from app.api.api_v1.endpoints import login, users, manga, chapters, bookmarks

api_router = APIRouter()
api_router.include_router(login.router, tags=["login"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(manga.router, prefix="/manga", tags=["manga"])
api_router.include_router(chapters.router, prefix="/chapters", tags=["chapters"])
api_router.include_router(bookmarks.router, prefix="/bookmarks", tags=["bookmarks"])