"""Job description Pydantic schemas."""

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class JobDescriptionBase(BaseModel):
    """Shared job description fields."""

    company: str
    role: str
    description_text: str
    experience_level: str | None = None
    url: str | None = None


class JobDescriptionCreate(JobDescriptionBase):
    """Schema for creating a job description."""

    pass


class JobDescriptionUpdate(BaseModel):
    """Schema for updating a job description. All fields optional."""

    company: str | None = None
    role: str | None = None
    description_text: str | None = None
    experience_level: str | None = None
    url: str | None = None


class JobDescriptionResponse(JobDescriptionBase):
    """Job description response."""

    id: uuid.UUID
    user_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
