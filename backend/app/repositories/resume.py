"""Resume repository."""

import uuid

from sqlalchemy import select, func

from app.models.resume import Resume
from app.repositories.base import BaseRepository


class ResumeRepository(BaseRepository[Resume]):
    """Repository for Resume operations."""

    model = Resume

    async def get_by_user_id(
        self, user_id: uuid.UUID, *, skip: int = 0, limit: int = 20
    ) -> list[Resume]:
        """Get all resumes for a user."""
        result = await self.db.execute(
            select(Resume)
            .where(Resume.user_id == user_id)
            .order_by(Resume.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def count_by_user_id(self, user_id: uuid.UUID) -> int:
        """Count resumes for a user."""
        result = await self.db.execute(
            select(func.count())
            .select_from(Resume)
            .where(Resume.user_id == user_id)
        )
        return result.scalar_one()

    async def clear_primary(self, user_id: uuid.UUID) -> None:
        """Clear the primary flag on all resumes for a user."""
        from sqlalchemy import update

        await self.db.execute(
            update(Resume)
            .where(Resume.user_id == user_id, Resume.is_primary.is_(True))
            .values(is_primary=False)
        )
