"""User service — user creation and retrieval."""

import structlog
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundException, ConflictException
from app.models.user import User
from app.repositories.user import UserRepository
from app.schemas.user import UserCreate

logger = structlog.get_logger()


class UserService:
    """Business logic for user operations."""

    def __init__(self, db: AsyncSession) -> None:
        self.repo = UserRepository(db)

    async def get_or_create_by_firebase(self, data: UserCreate) -> tuple[User, bool]:
        """Get existing user by Firebase UID, or create a new one.

        Returns (user, created) tuple.
        """
        existing = await self.repo.get_by_firebase_uid(data.firebase_uid)
        if existing:
            return existing, False

        # Check for email conflict
        email_user = await self.repo.get_by_email(data.email)
        if email_user:
            raise ConflictException(f"User with email '{data.email}' already exists")

        user = User(
            firebase_uid=data.firebase_uid,
            email=data.email,
            display_name=data.display_name,
            photo_url=data.photo_url,
        )
        created_user = await self.repo.create(user)
        logger.info("user_created", firebase_uid=data.firebase_uid, email=data.email)
        return created_user, True

    async def get_by_firebase_uid(self, firebase_uid: str) -> User:
        """Get a user by Firebase UID. Raises NotFoundException if not found."""
        user = await self.repo.get_by_firebase_uid(firebase_uid)
        if not user:
            raise NotFoundException("User", firebase_uid)
        return user
