"""Resume routes — upload, list, delete."""

import uuid

from fastapi import APIRouter, Depends, File, Form, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.dependencies import get_current_db_user
from app.models.user import User
from app.schemas.resume import ResumeListResponse, ResumeResponse
from app.services.resume import ResumeService

router = APIRouter()


@router.post(
    "",
    response_model=ResumeResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload resume",
)
async def upload_resume(
    file: UploadFile = File(..., description="Resume file (PDF or DOCX, max 10MB)"),
    is_primary: bool = Form(False, description="Set as primary resume"),
    current_user: User = Depends(get_current_db_user),
    db: AsyncSession = Depends(get_db),
) -> ResumeResponse:
    """Upload a resume file.

    Accepted formats: PDF, DOCX. Maximum size: 10MB.
    """
    service = ResumeService(db)
    resume = await service.upload(current_user.id, file, is_primary=is_primary)
    return ResumeResponse.model_validate(resume)


@router.get(
    "",
    response_model=ResumeListResponse,
    summary="List resumes",
)
async def list_resumes(
    current_user: User = Depends(get_current_db_user),
    db: AsyncSession = Depends(get_db),
) -> ResumeListResponse:
    """List all resumes for the current user."""
    service = ResumeService(db)
    resumes, total = await service.list_for_user(current_user.id)
    return ResumeListResponse(
        resumes=[ResumeResponse.model_validate(r) for r in resumes],
        total=total,
    )


@router.delete(
    "/{resume_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete resume",
)
async def delete_resume(
    resume_id: uuid.UUID,
    current_user: User = Depends(get_current_db_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    """Delete a resume. Only the owner can delete their resume."""
    service = ResumeService(db)
    await service.delete(resume_id, current_user.id)
