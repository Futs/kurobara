from typing import Literal
from enum import Enum
from pydantic import BaseModel, EmailStr, UUID4, Field, model_validator
from datetime import datetime


class Theme(str, Enum):
    DARK = "dark"
    LIGHT = "light"
    SYSTEM = "system"


class OAuthProvider(str, Enum):
    GOOGLE = "google"
    GITHUB = "github"
    DISCORD = "discord"


# Shared properties
class UserBase(BaseModel):
    email: EmailStr | None = None
    is_active: bool = True
    is_superuser: bool = False
    full_name: str | None = None
    blur_nsfw: bool = True
    show_explicit_on_dashboard: bool = False
    theme: Theme = Theme.DARK


# Properties to receive via API on creation
class UserCreate(UserBase):
    email: EmailStr
    password: str = Field(..., min_length=8)


# Properties to receive via API on update
class UserUpdate(UserBase):
    password: str | None = Field(None, min_length=8)
    two_factor_enabled: bool | None = None


# Properties to return via API
class User(UserBase):
    id: UUID4
    oauth_provider: OAuthProvider | None = None
    two_factor_enabled: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# Properties for OAuth login
class OAuthLogin(BaseModel):
    provider: OAuthProvider
    code: str
    redirect_uri: str | None = None


# Properties for 2FA setup
class TwoFactorSetup(BaseModel):
    enable: bool


# Properties for 2FA verification
class TwoFactorVerify(BaseModel):
    code: str = Field(..., min_length=6, max_length=6, pattern=r"^\d{6}$")


# Properties for user preferences
class UserPreferences(BaseModel):
    blur_nsfw: bool | None = None
    show_explicit_on_dashboard: bool | None = None
    theme: Theme | None = None