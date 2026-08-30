"""Resume service — upload, retrieval, and deletion."""

import uuid

import structlog
from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import (
    FileTooLargeException,
    ForbiddenException,
    InvalidFileTypeException,
    NotFoundException,
)
from app.infrastructure.storage import StorageBackend, get_storage
from app.models.resume import Resume
from app.repositories.resume import ResumeRepository

logger = structlog.get_logger()

# Allowed file types for resume upload
ALLOWED_CONTENT_TYPES = [
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",  # .docx
]
ALLOWED_EXTENSIONS = [".pdf", ".docx"]
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB


class ResumeService:
    """Business logic for resume operations."""

    def __init__(self, db: AsyncSession) -> None:
        self.repo = ResumeRepository(db)
        self.storage: StorageBackend = get_storage()

    async def upload(
        self,
        user_id: uuid.UUID,
        file: UploadFile,
        *,
        is_primary: bool = False,
    ) -> Resume:
        """Upload a resume file.

        Validates file type and size, stores the file, and creates a DB record.
        """
        # Validate file type
        filename = file.filename or "resume"
        if not any(filename.lower().endswith(ext) for ext in ALLOWED_EXTENSIONS):
            raise InvalidFileTypeException(ALLOWED_EXTENSIONS)

        if file.content_type and file.content_type not in ALLOWED_CONTENT_TYPES:
            raise InvalidFileTypeException(ALLOWED_EXTENSIONS)

        # Read file content
        content = await file.read()

        # Validate file size
        if len(content) > MAX_FILE_SIZE:
            raise FileTooLargeException(MAX_FILE_SIZE // (1024 * 1024))

        # Store file
        storage_path = f"resumes/{user_id}/{uuid.uuid4()}/{filename}"
        await self.storage.put(storage_path, content)

        # If setting as primary, clear existing primary
        if is_primary:
            await self.repo.clear_primary(user_id)

        # Create DB record
        resume = Resume(
            user_id=user_id,
            filename=filename,
            storage_path=storage_path,
            content_type=file.content_type or "application/octet-stream",
            file_size=len(content),
            is_primary=is_primary,
        )
        created = await self.repo.create(resume)
        logger.info(
            "resume_uploaded",
            user_id=str(user_id),
            filename=filename,
            size=len(content),
        )
        return created

    async def list_for_user(self, user_id: uuid.UUID) -> tuple[list[Resume], int]:
        """List all resumes for a user."""
        resumes = await self.repo.get_by_user_id(user_id)
        total = await self.repo.count_by_user_id(user_id)
        return resumes, total

    async def delete(self, resume_id: uuid.UUID, user_id: uuid.UUID) -> None:
        """Delete a resume. Enforces ownership."""
        resume = await self.repo.get_by_id(resume_id)
        if not resume:
            raise NotFoundException("Resume", str(resume_id))
        if resume.user_id != user_id:
            raise ForbiddenException()

        # Delete from storage
        await self.storage.delete(resume.storage_path)

        # Delete DB record
        await self.repo.delete(resume)
        logger.info(
            "resume_deleted", user_id=str(user_id), resume_id=str(resume_id)
        )
