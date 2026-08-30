"""Interview, interview plan, and transcript models — Phase 4 stubs."""

import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, Float, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, UUIDMixin, TimestampMixin


class InterviewMode(str, enum.Enum):
    """Interview mode: practice or simulation."""

    PRACTICE = "practice"
    SIMULATION = "simulation"


class InterviewStatus(str, enum.Enum):
    """Interview lifecycle status."""

    PLANNED = "planned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class Interview(Base, UUIDMixin, TimestampMixin):
    """An interview session — either focused practice or simulation."""

    __tablename__ = "interviews"

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    mode: Mapped[InterviewMode] = mapped_column(
        Enum(InterviewMode), nullable=False
    )
    status: Mapped[InterviewStatus] = mapped_column(
        Enum(InterviewStatus), default=InterviewStatus.PLANNED, nullable=False
    )
    company: Mapped[str | None] = mapped_column(String(255), nullable=True)
    role: Mapped[str | None] = mapped_column(String(255), nullable=True)
    experience_level: Mapped[str | None] = mapped_column(String(50), nullable=True)
    job_description_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("job_descriptions.id"), nullable=True
    )
    resume_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("resumes.id"), nullable=True
    )
    duration_minutes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    selected_question_types: Mapped[list | None] = mapped_column(JSONB, nullable=True)

    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Overall scores (populated after completion)
    overall_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    scores_by_competency: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    # Relationships
    questions: Mapped[list["InterviewQuestion"]] = relationship(
        "InterviewQuestion", back_populates="interview", cascade="all, delete-orphan"
    )
    plan: Mapped["InterviewPlan | None"] = relationship(
        "InterviewPlan", back_populates="interview", uselist=False, cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Interview {self.mode.value} — {self.status.value}>"


class InterviewPlan(Base, UUIDMixin, TimestampMixin):
    """The interview blueprint — sequence of competencies/question types to cover."""

    __tablename__ = "interview_plans"

    interview_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("interviews.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )
    plan_data: Mapped[dict] = mapped_column(JSONB, nullable=False)

    # Relationships
    interview: Mapped["Interview"] = relationship("Interview", back_populates="plan")
    items: Mapped[list["InterviewPlanItem"]] = relationship(
        "InterviewPlanItem", back_populates="plan", cascade="all, delete-orphan"
    )


class InterviewPlanItem(Base, UUIDMixin, TimestampMixin):
    """Individual item in an interview plan — a competency/question type to cover."""

    __tablename__ = "interview_plan_items"

    plan_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("interview_plans.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    order: Mapped[int] = mapped_column(Integer, nullable=False)
    question_type: Mapped[str] = mapped_column(String(100), nullable=False)
    competency: Mapped[str | None] = mapped_column(String(255), nullable=True)
    allocated_minutes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    is_completed: Mapped[bool] = mapped_column(default=False, nullable=False)

    # Relationships
    plan: Mapped["InterviewPlan"] = relationship("InterviewPlan", back_populates="items")


class InterviewQuestion(Base, UUIDMixin, TimestampMixin):
    """A question asked during an interview."""

    __tablename__ = "interview_questions"

    interview_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("interviews.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    parent_question_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("interview_questions.id"), nullable=True
    )
    question_text: Mapped[str] = mapped_column(Text, nullable=False)
    question_type: Mapped[str] = mapped_column(String(100), nullable=False)
    competencies: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    difficulty: Mapped[int | None] = mapped_column(Integer, nullable=True)
    order: Mapped[int] = mapped_column(Integer, nullable=False)

    # Source tracking
    source_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    selection_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    confidence: Mapped[float | None] = mapped_column(Float, nullable=True)

    # Relationships
    interview: Mapped["Interview"] = relationship("Interview", back_populates="questions")
    answer: Mapped["Answer | None"] = relationship(
        "Answer", back_populates="question", uselist=False, cascade="all, delete-orphan"
    )
    follow_ups: Mapped[list["InterviewQuestion"]] = relationship(
        "InterviewQuestion",
        backref="parent_question",
        remote_side="InterviewQuestion.id",
    )


class Answer(Base, UUIDMixin, TimestampMixin):
    """Candidate's answer to an interview question."""

    __tablename__ = "answers"

    question_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("interview_questions.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )
    answer_text: Mapped[str] = mapped_column(Text, nullable=False)
    duration_seconds: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Relationships
    question: Mapped["InterviewQuestion"] = relationship(
        "InterviewQuestion", back_populates="answer"
    )
    evaluation: Mapped["Evaluation | None"] = relationship(
        "Evaluation", back_populates="answer", uselist=False, cascade="all, delete-orphan"
    )


class Evaluation(Base, UUIDMixin, TimestampMixin):
    """AI evaluation of a candidate's answer."""

    __tablename__ = "evaluations"

    answer_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("answers.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )
    score: Mapped[float] = mapped_column(Float, nullable=False)
    max_score: Mapped[float] = mapped_column(Float, default=10.0, nullable=False)
    feedback: Mapped[str] = mapped_column(Text, nullable=False)
    strengths: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    weaknesses: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    criteria_scores: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    follow_up_reason: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationships
    answer: Mapped["Answer"] = relationship("Answer", back_populates="evaluation")

    def __repr__(self) -> str:
        return f"<Evaluation score={self.score}/{self.max_score}>"
