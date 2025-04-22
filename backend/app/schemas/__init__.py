from pydantic import BaseModel

from .token import Token, TokenPayload
from .user import User, UserCreate, UserUpdate, UserPreferences, OAuthLogin, TwoFactorSetup, TwoFactorVerify
from .manga import (
    Manga, MangaCreate, MangaUpdate, 
    Chapter, ChapterCreate, ChapterUpdate,
    Bookmark, BookmarkCreate, BookmarkUpdate,
    MangaSearch, MangaSearchResult, UserMangaInfo,
    MangaShare, MangaShareLink
)


class Msg(BaseModel):
    msg: str