"""Candidate profile routes."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.dependencies import get_current_db_user
from app.models.user import User
from app.schemas.candidate import (
    CandidateProfileResponse,
    CandidateProfileUpdate,
)
from app.services.candidate import CandidateService

router = APIRouter()


@router.get(
    "",
    response_model=CandidateProfileResponse,
    summary="Get candidate profile",
)
async def get_profile(
    current_user: User = Depends(get_current_db_user),
    db: AsyncSession = Depends(get_db),
) -> CandidateProfileResponse:
    """Get the current user's candidate profile."""
    service = CandidateService(db)
    profile, _ = await service.get_or_create_profile(current_user.id)
    return CandidateProfileResponse.model_validate(profile)


@router.put(
    "",
    response_model=CandidateProfileResponse,
    summary="Update candidate profile",
)
async def update_profile(
    data: CandidateProfileUpdate,
    current_user: User = Depends(get_current_db_user),
    db: AsyncSession = Depends(get_db),
) -> CandidateProfileResponse:
    """Update the current user's candidate profile.

    Creates the profile if it doesn't exist (upsert behavior).
    """
    service = CandidateService(db)
    profile = await service.update_profile(current_user.id, data)
    return CandidateProfileResponse.model_validate(profile)
