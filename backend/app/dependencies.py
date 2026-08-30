"""FastAPI dependency injection."""

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends

from app.core.database import get_db
from app.core.security import FirebaseUser, get_current_user
from app.models.user import User
from app.services.user import UserService


async def get_current_db_user(
    firebase_user: FirebaseUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> User:
    """Get the current authenticated user's DB record.

    Combines Firebase auth verification with PostgreSQL user lookup.
    Raises 401 if token is invalid, 404 if user not found in DB.
    """
    user_service = UserService(db)
    try:
        return await user_service.get_by_firebase_uid(firebase_user.uid)
    except Exception:
        user, _ = await user_service.get_or_create_by_firebase(
            UserCreate(
                firebase_uid=firebase_user.uid,
                email=firebase_user.email or f"{firebase_user.uid}@placeholder.com",
                display_name=firebase_user.name,
            )
        )
        return user
