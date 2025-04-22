from typing import List, Dict, Any, Literal, Annotated
from enum import Enum
from pydantic import BaseModel, Field, HttpUrl, UUID4, model_validator
from datetime import datetime


class PublicationDemographic(str, Enum):
    SHOUNEN = "shounen"
    SHOUJO = "shoujo"
    SEINEN = "seinen"
    JOSEI = "josei"
    NONE = "none"


class ContentRating(str, Enum):
    SAFE = "safe"
    SUGGESTIVE = "suggestive"
    NSFW = "nsfw"
    EXPLICIT = "explicit"


class MangaStatus(str, Enum):
    ONGOING = "ongoing"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    HIATUS = "hiatus"


class ReadingStatus(str, Enum):
    PLAN_TO_READ = "plan_to_read"
    READING = "reading"
    ON_HOLD = "on_hold"
    COMPLETED = "completed"
    DROPPED = "dropped"


# Shared properties
class MangaBase(BaseModel):
    title: str
    alternative_titles: Dict[str, str] | None = None
    description: str | None = None
    status: MangaStatus | None = MangaStatus.ONGOING
    publication_demographic: PublicationDemographic | None = None
    content_rating: ContentRating | None = ContentRating.SAFE
    is_nsfw: bool = False
    is_explicit: bool = False
    author: str | None = None
    artist: str | None = None
    year: int | None = None
    tags: List[str] | None = None
    genres: List[str] | None = None
    source_url: HttpUrl | None = None
    source_id: str | None = None
    source_name: str | None = None

    @model_validator(mode='after')
    def validate_nsfw_flags(self):
        if self.content_rating in [ContentRating.NSFW, ContentRating.EXPLICIT]:
            self.is_nsfw = True
        if self.content_rating == ContentRating.EXPLICIT:
            self.is_explicit = True
        return self


# Properties to receive on manga creation
class MangaCreate(MangaBase):
    pass


# Properties to receive on manga update
class MangaUpdate(MangaBase):
    title: str | None = None


# Properties to return via API
class Manga(MangaBase):
    id: UUID4
    cover_image: str | None = None
    created_at: datetime
    updated_at: datetime
    
    model_config = {"from_attributes": True}


# Shared properties for Chapter
class ChapterBase(BaseModel):
    chapter_number: float
    title: str | None = None
    pages_count: int = 0
    source_url: HttpUrl | None = None
    published_at: datetime | None = None


# Properties to receive on chapter creation
class ChapterCreate(ChapterBase):
    manga_id: UUID4


# Properties to receive on chapter update
class ChapterUpdate(ChapterBase):
    chapter_number: float | None = None
    is_downloaded: bool | None = None
    download_path: str | None = None


# Properties to return via API
class Chapter(ChapterBase):
    id: UUID4
    manga_id: UUID4
    is_downloaded: bool
    download_path: str | None = None
    created_at: datetime
    updated_at: datetime
    
    model_config = {"from_attributes": True}


# Shared properties for Bookmark
class BookmarkBase(BaseModel):
    page_number: int
    note: str | None = None


# Properties to receive on bookmark creation
class BookmarkCreate(BookmarkBase):
    manga_id: UUID4
    chapter_id: UUID4


# Properties to receive on bookmark update
class BookmarkUpdate(BookmarkBase):
    pass


# Properties to return via API
class Bookmark(BookmarkBase):
    id: UUID4
    user_id: UUID4
    manga_id: UUID4
    chapter_id: UUID4
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