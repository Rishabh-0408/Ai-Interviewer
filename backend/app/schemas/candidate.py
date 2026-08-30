"""Candidate profile Pydantic schemas."""

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class CandidateProfileBase(BaseModel):
    """Shared candidate profile fields."""

    experience_level: str | None = None
    target_role: str | None = None
    target_company: str | None = None
    bio: str | None = None
    years_of_experience: int | None = None
    current_role: str | None = None
    current_company: str | None = None


class CandidateProfileCreate(CandidateProfileBase):
    """Schema for creating a candidate profile."""

    pass


class CandidateProfileUpdate(CandidateProfileBase):
    """Schema for updating a candidate profile. All fields optional."""

    pass


class CandidateProfileResponse(CandidateProfileBase):
    """Candidate profile response."""

    id: uuid.UUID
    user_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
