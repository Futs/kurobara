from typing import Literal
from pydantic import BaseModel, Field


class Token(BaseModel):
    access_token: str
    token_type: Literal["bearer"] = "bearer"
    requires_two_factor: bool = False


class TokenPayload(BaseModel):
    sub: str | None = None
    two_factor_verified: bool = False
    exp: int | None = None