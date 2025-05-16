from typing import List, Optional
from enum import Enum
from pydantic import BaseModel, UUID4, Field, field_validator, model_validator
from datetime import datetime
import re


class MangaStatus(str, Enum):
    ONGOING = "ongoing"
    COMPLETED = "completed"
    HIATUS = "hiatus"
    CANCELLED = "cancelled"


class ReadingStatus(str, Enum):
    READING = "reading"
    COMPLETED = "completed"
    ON_HOLD = "on_hold"
    DROPPED = "dropped"
    PLAN_TO_READ = "plan_to_read"


# Shared properties
class MangaBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    author: str = Field(..., min_length=1, max_length=100)
    artist: str | None = Field(None, max_length=100)
    description: str | None = Field(None, max_length=5000)
    status: MangaStatus = MangaStatus.ONGOING
    year: int | None = Field(None, ge=1900, le=datetime.now().year)
    genres: List[str] = []
    
    @field_validator('title')
    @classmethod
    def validate_title(cls, v: str) -> str:
        if len(v.strip()) == 0:
            raise ValueError('Title cannot be empty')
        return v.strip()
    
    @field_validator('author')
    @classmethod
    def validate_author(cls, v: str) -> str:
        if len(v.strip()) == 0:
            raise ValueError('Author cannot be empty')
        return v.strip()
    
    @field_validator('genres')
    @classmethod
    def validate_genres(cls, v: List[str]) -> List[str]:
        # Remove duplicates and empty strings
        return list(set(genre.strip() for genre in v if genre.strip()))


# Properties to receive on manga creation
class MangaCreate(MangaBase):
    pass


# Properties to receive on manga update
class MangaUpdate(MangaBase):
    title: str | None = Field(None, min_length=1, max_length=255)
    author: str | None = Field(None, min_length=1, max_length=100)
    status: MangaStatus | None = None
    
    @model_validator(mode='after')
    def check_at_least_one_field(self) -> 'MangaUpdate':
        fields = [self.title, self.author, self.artist, self.description, 
                 self.status, self.year]
        if all(f is None for f in fields) and not self.genres:
            raise ValueError('At least one field must be provided for update')
        return self


# Properties shared by models stored in DB
class MangaInDBBase(MangaBase):
    id: UUID4
    created_at: datetime
    updated_at: datetime
    
    model_config = {"from_attributes": True}


# Properties to return to client
class Manga(MangaInDBBase):
    pass


# Properties for manga in user collection
class UserManga(BaseModel):
    manga_id: UUID4
    reading_status: ReadingStatus = ReadingStatus.PLAN_TO_READ
    is_favorite: bool = False
    last_read_chapter: UUID4 | None = None
    last_read_page: int | None = Field(None, ge=1)
    
    @field_validator('last_read_page')
    @classmethod
    def validate_page(cls, v: Optional[int], values: dict) -> Optional[int]:
        if v is not None and values.get('last_read_chapter') is None:
            raise ValueError('Cannot set last_read_page without last_read_chapter')
        if v is not None and v < 1:
            raise ValueError('Page number must be positive')
        return v


# Properties for bookmarks
class BookmarkBase(BaseModel):
    manga_id: UUID4
    chapter_id: UUID4
    page_number: int = Field(..., ge=1)
    note: str | None = Field(None, max_length=500)


class BookmarkCreate(BookmarkBase):
    pass


class BookmarkUpdate(BaseModel):
    page_number: int | None = Field(None, ge=1)
    note: str | None = Field(None, max_length=500)
    
    @model_validator(mode='after')
    def check_at_least_one_field(self) -> 'BookmarkUpdate':
        if self.page_number is None and self.note is None:
            raise ValueError('At least one field must be provided for update')
        return self


class Bookmark(BookmarkBase):
    id: UUID4
    user_id: UUID4
    created_at: datetime
    updated_at: datetime
    
    model_config = {"from_attributes": True}


# Properties for manga search
class MangaSearch(BaseModel):
    query: str
    include_nsfw: bool = False
    include_explicit: bool = False


# Properties for manga search result
class MangaSearchResult(BaseModel):
    manga: Manga
    accuracy: float  # Search accuracy score


# Properties for user manga collection
class UserMangaInfo(BaseModel):
    manga_id: UUID4
    is_favorite: bool
    is_monitored: bool
    monitor_frequency: Annotated[int, Field(ge=0, le=7)]
    last_read_chapter: int | None = None
    last_read_page: int | None = None
    reading_status: ReadingStatus
    added_at: datetime


# Properties for manga sharing
class MangaShare(BaseModel):
    manga_id: UUID4
    expiration: datetime | None = None
    allow_download: bool = False


# Properties for shared manga link
class MangaShareLink(BaseModel):
    id: UUID4
    url: str
    expires_at: datetime | None = None
