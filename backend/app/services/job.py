"""Job description service."""

import uuid

import structlog
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ForbiddenException, NotFoundException
from app.models.job import JobDescription
from app.repositories.job import JobRepository
from app.schemas.job import JobDescriptionCreate, JobDescriptionUpdate

logger = structlog.get_logger()


class JobService:
    """Business logic for job description operations."""

    def __init__(self, db: AsyncSession) -> None:
        self.repo = JobRepository(db)

    async def create(
        self, user_id: uuid.UUID, data: JobDescriptionCreate
    ) -> JobDescription:
        """Create a new job description."""
        job = JobDescription(
            user_id=user_id,
            **data.model_dump(),
        )
        created = await self.repo.create(job)
        logger.info(
            "job_description_created",
            user_id=str(user_id),
            company=data.company,
            role=data.role,
        )
        return created

    async def list_for_user(
        self, user_id: uuid.UUID, *, skip: int = 0, limit: int = 20
    ) -> tuple[list[JobDescription], int]:
        """List job descriptions for a user."""
        jobs = await self.repo.get_by_user_id(user_id, skip=skip, limit=limit)
        total = await self.repo.count_by_user_id(user_id)
        return jobs, total

    async def get_for_user(
        self, job_id: uuid.UUID, user_id: uuid.UUID
    ) -> JobDescription:
        """Get a specific job description with ownership check."""
        job = await self.repo.get_by_id_and_user(job_id, user_id)
        if not job:
            raise NotFoundException("Job description", str(job_id))
        return job

    async def update(
        self, job_id: uuid.UUID, user_id: uuid.UUID, data: JobDescriptionUpdate
    ) -> JobDescription:
        """Update a job description with ownership check."""
        job = await self.get_for_user(job_id, user_id)
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(job, field, value)
        return await self.repo.update(job)

    async def delete(self, job_id: uuid.UUID, user_id: uuid.UUID) -> None:
        """Delete a job description with ownership check."""
        job = await self.get_for_user(job_id, user_id)
        await self.repo.delete(job)
        logger.info(
            "job_description_deleted",
            user_id=str(user_id),
            job_id=str(job_id),
        )
