"""Candidate profile model."""

import uuid

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, UUIDMixin, TimestampMixin


class CandidateProfile(Base, UUIDMixin, TimestampMixin):
    """Extended profile for a candidate user.

    Contains interview preparation context: target role, company,
    experience level, and bio.
    """

    __tablename__ = "candidate_profiles"

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
    )
    experience_level: Mapped[str | None] = mapped_column(
        String(50), nullable=True
    )  # e.g. "junior", "mid", "senior", "staff", "principal"
    target_role: Mapped[str | None] = mapped_column(String(255), nullable=True)
    target_company: Mapped[str | None] = mapped_column(String(255), nullable=True)
    bio: Mapped[str | None] = mapped_column(Text, nullable=True)
    years_of_experience: Mapped[int | None] = mapped_column(nullable=True)
    current_role: Mapped[str | None] = mapped_column(String(255), nullable=True)
    current_company: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="candidate_profile")

    def __repr__(self) -> str:
        return f"<CandidateProfile user_id={self.user_id} target_role={self.target_role!r}>"


from app.models.user import User  # noqa: E402, F401
