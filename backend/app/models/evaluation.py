"""Evaluation rubrics, candidate skill profiles, and performance models."""

import uuid

from sqlalchemy import Float, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, UUIDMixin, TimestampMixin


class EvaluationRubric(Base, UUIDMixin, TimestampMixin):
    """Evaluation rubric for a specific question type.

    Different question types use different rubrics per spec Section 26.
    """

    __tablename__ = "evaluation_rubrics"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    question_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationships
    criteria: Mapped[list["RubricCriteria"]] = relationship(
        "RubricCriteria", back_populates="rubric", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<EvaluationRubric {self.name} ({self.question_type})>"


class RubricCriteria(Base, UUIDMixin, TimestampMixin):
    """Individual criterion within an evaluation rubric."""

    __tablename__ = "rubric_criteria"

    rubric_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("evaluation_rubrics.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    weight: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)
    max_score: Mapped[float] = mapped_column(Float, default=10.0, nullable=False)

    # Relationships
    rubric: Mapped["EvaluationRubric"] = relationship(
        "EvaluationRubric", back_populates="criteria"
    )


class CandidateSkillProfile(Base, UUIDMixin, TimestampMixin):
    """Aggregated skill profile for a candidate — built from interview performance."""

    __tablename__ = "candidate_skill_profiles"

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    competency: Mapped[str] = mapped_column(String(255), nullable=False)
    current_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    total_assessments: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    trend: Mapped[str | None] = mapped_column(String(50), nullable=True)  # improving, stable, declining
    score_history: Mapped[list | None] = mapped_column(JSONB, nullable=True)


class CandidatePerformance(Base, UUIDMixin, TimestampMixin):
    """Per-interview performance record for longitudinal tracking."""

    __tablename__ = "candidate_performance"

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    interview_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("interviews.id", ondelete="CASCADE"),
        nullable=False,
    )
    competency: Mapped[str] = mapped_column(String(255), nullable=False)
    score: Mapped[float] = mapped_column(Float, nullable=False)
    max_score: Mapped[float] = mapped_column(Float, default=10.0, nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
