"""Resume Pydantic schemas."""

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ResumeResponse(BaseModel):
    """Resume response schema."""

    id: uuid.UUID
    filename: str
    content_type: str
    file_size: int
    is_primary: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ResumeListResponse(BaseModel):
    """List of resumes."""

    resumes: list[ResumeResponse]
    total: int
