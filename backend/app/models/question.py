"""Question intelligence, taxonomy, and competency models — Phase 3 stubs."""

import enum

from sqlalchemy import Enum, Float, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from pgvector.sqlalchemy import Vector

from app.models.base import Base, UUIDMixin, TimestampMixin


class QuestionTypeEnum(str, enum.Enum):
    """Supported question types per spec Section 9."""

    TECHNICAL = "TECHNICAL"
    BEHAVIORAL = "BEHAVIORAL"
    ANALYTICAL = "ANALYTICAL"
    CASE_STUDY = "CASE_STUDY"
    SITUATIONAL = "SITUATIONAL"
    PERSONAL_MOTIVATIONAL = "PERSONAL_MOTIVATIONAL"
    HR_CULTURE = "HR_CULTURE"
    COMMUNICATION = "COMMUNICATION"
    CURVEBALL_STRESS = "CURVEBALL_STRESS"
    SALARY_LOGISTICS = "SALARY_LOGISTICS"
    LEADERSHIP_TEAMWORK = "LEADERSHIP_TEAMWORK"
    ETHICAL_INTEGRITY = "ETHICAL_INTEGRITY"
    REFLECTIVE_SELF_GROWTH = "REFLECTIVE_SELF_GROWTH"
    RAPID_FIRE_ICEBREAKER = "RAPID_FIRE_ICEBREAKER"
    FOLLOW_UP_PROBING = "FOLLOW_UP_PROBING"


class SourceType(str, enum.Enum):
    """Evidence source types per spec Section 14."""

    OFFICIAL = "OFFICIAL"
    PUBLICLY_REPORTED = "PUBLICLY_REPORTED"
    PLATFORM_DATA = "PLATFORM_DATA"
    GENERAL_ROLE_KNOWLEDGE = "GENERAL_ROLE_KNOWLEDGE"
    AI_GENERATED = "AI_GENERATED"


class Competency(Base, UUIDMixin, TimestampMixin):
    """A skill or competency area (e.g., System Design, Conflict Resolution)."""

    __tablename__ = "competencies"

    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    category: Mapped[str | None] = mapped_column(String(100), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    def __repr__(self) -> str:
        return f"<Competency {self.name}>"


class QuestionIntelligence(Base, UUIDMixin, TimestampMixin):
    """Question intelligence record — the core differentiator.

    Stores question patterns with metadata, evidence provenance,
    relevance scores, and embeddings for semantic retrieval.
    """

    __tablename__ = "question_intelligence"

    question_text: Mapped[str] = mapped_column(Text, nullable=False)
    question_type: Mapped[QuestionTypeEnum] = mapped_column(
        Enum(QuestionTypeEnum), nullable=False, index=True
    )
    role: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    company: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    experience_level: Mapped[str | None] = mapped_column(String(50), nullable=True)
    competencies: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    difficulty: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Relevance scores
    frequency: Mapped[float | None] = mapped_column(Float, nullable=True)
    importance: Mapped[float | None] = mapped_column(Float, nullable=True)
    role_relevance: Mapped[float | None] = mapped_column(Float, nullable=True)
    company_relevance: Mapped[float | None] = mapped_column(Float, nullable=True)
    core_concept_relevance: Mapped[float | None] = mapped_column(Float, nullable=True)
    trend_relevance: Mapped[float | None] = mapped_column(Float, nullable=True)

    # Source provenance
    source_type: Mapped[SourceType | None] = mapped_column(Enum(SourceType), nullable=True)
    source_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    source_date: Mapped[str | None] = mapped_column(String(50), nullable=True)
    confidence: Mapped[float | None] = mapped_column(Float, nullable=True)

    # Vector embedding for semantic search (1536 dimensions — OpenAI compatible)
    embedding: Mapped[list | None] = mapped_column(Vector(1536), nullable=True)

    def __repr__(self) -> str:
        return f"<QuestionIntelligence {self.question_type.value}: {self.question_text[:50]}>"


class QuestionObservation(Base, UUIDMixin, TimestampMixin):
    """Individual observation about a question — from research sources.

    Tracks provenance per spec Section 14.
    """

    __tablename__ = "question_observations"

    source_type: Mapped[SourceType] = mapped_column(Enum(SourceType), nullable=False)
    source_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    source_title: Mapped[str | None] = mapped_column(String(500), nullable=True)
    source_date: Mapped[str | None] = mapped_column(String(50), nullable=True)
    retrieved_at: Mapped[str | None] = mapped_column(String(50), nullable=True)
    company: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    role: Mapped[str | None] = mapped_column(String(255), nullable=True)
    claim: Mapped[str] = mapped_column(Text, nullable=False)
    confidence: Mapped[float | None] = mapped_column(Float, nullable=True)

    def __repr__(self) -> str:
        return f"<QuestionObservation {self.source_type.value}: {self.claim[:50]}>"
