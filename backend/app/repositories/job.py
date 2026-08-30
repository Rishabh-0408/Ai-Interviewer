"""Job description repository."""

import uuid

from sqlalchemy import select, func

from app.models.job import JobDescription
from app.repositories.base import BaseRepository


class JobRepository(BaseRepository[JobDescription]):
    """Repository for JobDescription operations."""

    model = JobDescription

    async def get_by_user_id(
        self, user_id: uuid.UUID, *, skip: int = 0, limit: int = 20
    ) -> list[JobDescription]:
        """Get all job descriptions for a user."""
        result = await self.db.execute(
            select(JobDescription)
            .where(JobDescription.user_id == user_id)
            .order_by(JobDescription.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def count_by_user_id(self, user_id: uuid.UUID) -> int:
        """Count job descriptions for a user."""
        result = await self.db.execute(
            select(func.count())
            .select_from(JobDescription)
            .where(JobDescription.user_id == user_id)
        )
        return result.scalar_one()

    async def get_by_id_and_user(
        self, id: uuid.UUID, user_id: uuid.UUID
    ) -> JobDescription | None:
        """Get a job description by ID, scoped to a specific user (ownership check)."""
        result = await self.db.execute(
            select(JobDescription).where(
                JobDescription.id == id,
                JobDescription.user_id == user_id,
            )
        )
        return result.scalar_one_or_none()
