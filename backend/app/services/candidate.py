"""Candidate profile service."""

import uuid

import structlog
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundException
from app.models.candidate import CandidateProfile
from app.repositories.candidate import CandidateRepository
from app.schemas.candidate import CandidateProfileCreate, CandidateProfileUpdate

logger = structlog.get_logger()


class CandidateService:
    """Business logic for candidate profile operations."""

    def __init__(self, db: AsyncSession) -> None:
        self.repo = CandidateRepository(db)

    async def get_profile(self, user_id: uuid.UUID) -> CandidateProfile:
        """Get candidate profile by user ID. Raises NotFoundException if not found."""
        profile = await self.repo.get_by_user_id(user_id)
        if not profile:
            raise NotFoundException("Candidate profile")
        return profile

    async def get_or_create_profile(
        self, user_id: uuid.UUID, data: CandidateProfileCreate | None = None
    ) -> tuple[CandidateProfile, bool]:
        """Get existing profile or create a new one."""
        existing = await self.repo.get_by_user_id(user_id)
        if existing:
            return existing, False

        profile = CandidateProfile(
            user_id=user_id,
            **(data.model_dump(exclude_unset=True) if data else {}),
        )
        created = await self.repo.create(profile)
        logger.info("candidate_profile_created", user_id=str(user_id))
        return created, True

    async def update_profile(
        self, user_id: uuid.UUID, data: CandidateProfileUpdate
    ) -> CandidateProfile:
        """Update candidate profile. Creates one if it doesn't exist."""
        profile = await self.repo.get_by_user_id(user_id)

        if not profile:
            profile = CandidateProfile(user_id=user_id)
            self.repo.db.add(profile)

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(profile, field, value)

        return await self.repo.update(profile)
