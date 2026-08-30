"""Job description routes."""

import uuid

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.dependencies import get_current_db_user
from app.models.user import User
from app.schemas.job import (
    JobDescriptionCreate,
    JobDescriptionResponse,
)

from app.services.job import JobService

router = APIRouter()


@router.post(
    "",
    response_model=JobDescriptionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create job description",
)
async def create_job(
    data: JobDescriptionCreate,
    current_user: User = Depends(get_current_db_user),
    db: AsyncSession = Depends(get_db),
) -> JobDescriptionResponse:
    """Create a new job description for interview preparation."""
    service = JobService(db)
    job = await service.create(current_user.id, data)
    return JobDescriptionResponse.model_validate(job)


@router.get(
    "",
    response_model=list[JobDescriptionResponse],
    summary="List job descriptions",
)
async def list_jobs(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_db_user),
    db: AsyncSession = Depends(get_db),
) -> list[JobDescriptionResponse]:
    """List all job descriptions for the current user."""
    service = JobService(db)
    jobs, _ = await service.list_for_user(current_user.id, skip=skip, limit=limit)
    return [JobDescriptionResponse.model_validate(j) for j in jobs]


@router.get(
    "/{job_id}",
    response_model=JobDescriptionResponse,
    summary="Get job description",
)
async def get_job(
    job_id: uuid.UUID,
    current_user: User = Depends(get_current_db_user),
    db: AsyncSession = Depends(get_db),
) -> JobDescriptionResponse:
    """Get a specific job description (ownership enforced)."""
    service = JobService(db)
    job = await service.get_for_user(job_id, current_user.id)
    return JobDescriptionResponse.model_validate(job)
