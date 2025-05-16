from typing import Generic, TypeVar, List, Optional
from pydantic import BaseModel, Field

T = TypeVar('T')

class PaginationParams(BaseModel):
    skip: int = Field(0, ge=0, description="Number of items to skip")
    limit: int = Field(100, ge=1, le=100, description="Maximum number of items to return")

class PaginatedResponse(BaseModel, Generic[T]):
    data: List[T]
    total: int
    skip: int
    limit: int