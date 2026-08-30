"""User model — linked to Firebase Auth via firebase_uid."""

import uuid

from sqlalchemy import Boolean, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, UUIDMixin, TimestampMixin


class User(Base, UUIDMixin, TimestampMixin):
    """Application user, synced from Firebase Authentication.

    Every API request verifies the Firebase ID token and maps it
    to this PostgreSQL record via firebase_uid.
    """

    __tablename__ = "users"

    firebase_uid: Mapped[str] = mapped_column(
        String(128), unique=True, nullable=False, index=True
    )
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    display_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    photo_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Relationships
    candidate_profile: Mapped["CandidateProfile | None"] = relationship(
        "CandidateProfile", back_populates="user", uselist=False, lazy="selectin"
    )
    resumes: Mapped[list["Resume"]] = relationship(
        "Resume", back_populates="user", lazy="selectin"
    )
    job_descriptions: Mapped[list["JobDescription"]] = relationship(
        "JobDescription", back_populates="user", lazy="selectin"
    )

    def __repr__(self) -> str:
        return f"<User {self.email}>"


# Forward references resolved by SQLAlchemy automatically
from app.models.candidate import CandidateProfile  # noqa: E402, F401
from app.models.resume import Resume  # noqa: E402, F401
from app.models.job import JobDescription  # noqa: E402, F401
