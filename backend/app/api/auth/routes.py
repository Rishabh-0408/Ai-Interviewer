"""Authentication routes — register and get current user."""

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import FirebaseUser, get_current_user
from app.schemas.user import UserCreate, UserResponse, UserWithProfile
from app.services.user import UserService

router = APIRouter()


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register or sync user from Firebase",
)
async def register_user(
    firebase_user: FirebaseUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> UserResponse:
    """Register a new user or sync existing Firebase user to PostgreSQL.

    Called after Firebase client-side authentication to ensure the user
    exists in the application database.
    """
    service = UserService(db)
    user, created = await service.get_or_create_by_firebase(
        UserCreate(
            firebase_uid=firebase_user.uid,
            email=firebase_user.email or "",
            display_name=firebase_user.name,
        )
    )
    return UserResponse.model_validate(user)


@router.get(
    "/me",
    response_model=UserWithProfile,
    summary="Get current user",
)
async def get_me(
    firebase_user: FirebaseUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> UserWithProfile:
    """Get the current authenticated user with their candidate profile."""
    service = UserService(db)
    user = await service.get_by_firebase_uid(firebase_user.uid)
    return UserWithProfile.model_validate(user)
