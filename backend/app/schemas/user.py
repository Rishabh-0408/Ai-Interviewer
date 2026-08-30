"""User Pydantic schemas."""

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr


class UserBase(BaseModel):
    """Shared user fields."""

    email: str
    display_name: str | None = None
    photo_url: str | None = None


class UserCreate(BaseModel):
    """Schema for creating a user from Firebase auth sync."""

    firebase_uid: str
    email: str
    display_name: str | None = None
    photo_url: str | None = None


class UserResponse(UserBase):
    """User response schema."""

    id: uuid.UUID
    firebase_uid: str
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserWithProfile(UserResponse):
    """User response including candidate profile."""

    candidate_profile: "CandidateProfileResponse | None" = None


from app.schemas.candidate import CandidateProfileResponse  # noqa: E402, F401

UserWithProfile.model_rebuild()
