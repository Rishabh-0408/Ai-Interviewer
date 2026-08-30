"""Candidate profile repository."""

import uuid

from sqlalchemy import select

from app.models.candidate import CandidateProfile
from app.repositories.base import BaseRepository


class CandidateRepository(BaseRepository[CandidateProfile]):
    """Repository for CandidateProfile operations."""

    model = CandidateProfile

    async def get_by_user_id(self, user_id: uuid.UUID) -> CandidateProfile | None:
        """Get candidate profile by user ID."""
        result = await self.db.execute(
            select(CandidateProfile).where(CandidateProfile.user_id == user_id)
        )
        return result.scalar_one_or_none()
