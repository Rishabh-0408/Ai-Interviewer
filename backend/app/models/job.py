"""Job description and requirements models."""

import uuid

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, UUIDMixin, TimestampMixin


class JobDescription(Base, UUIDMixin, TimestampMixin):
    """A job description provided by a candidate for interview preparation.

    Contains the target company, role, description text, and experience level.
    """

    __tablename__ = "job_descriptions"

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    company: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(255), nullable=False)
    description_text: Mapped[str] = mapped_column(Text, nullable=False)
    experience_level: Mapped[str | None] = mapped_column(String(50), nullable=True)
    url: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="job_descriptions")
    requirements: Mapped[list["JobRequirement"]] = relationship(
        "JobRequirement", back_populates="job_description", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<JobDescription {self.company} — {self.role}>"


class JobRequirement(Base, UUIDMixin, TimestampMixin):
    """Individual requirement extracted from a job description."""

    __tablename__ = "job_requirements"

    job_description_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("job_descriptions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    requirement_text: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[str | None] = mapped_column(String(100), nullable=True)
    is_required: Mapped[bool] = mapped_column(default=True, nullable=False)

    # Relationships
    job_description: Mapped["JobDescription"] = relationship(
        "JobDescription", back_populates="requirements"
    )

    def __repr__(self) -> str:
        return f"<JobRequirement {self.requirement_text[:50]}>"


from app.models.user import User  # noqa: E402, F401
