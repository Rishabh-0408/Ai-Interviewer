"""Organization and organization profile models."""

from sqlalchemy import Float, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, UUIDMixin, TimestampMixin


class Organization(Base, UUIDMixin, TimestampMixin):
    """A company/organization that candidates target for interviews."""

    __tablename__ = "organizations"

    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    domain: Mapped[str | None] = mapped_column(String(255), nullable=True)
    career_page_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    industry: Mapped[str | None] = mapped_column(String(100), nullable=True)
    size: Mapped[str | None] = mapped_column(String(50), nullable=True)  # e.g. "1000-5000"
    values: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    def __repr__(self) -> str:
        return f"<Organization {self.name}>"


class OrganizationProfile(Base, UUIDMixin, TimestampMixin):
    """Research-based interview profile for an organization + role combination.

    Built by the research module from official sources, public reports, and platform data.
    """

    __tablename__ = "organization_profiles"

    organization_name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    role: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    experience_level: Mapped[str | None] = mapped_column(String(50), nullable=True)

    # Weights (how much emphasis the company places on each area)
    technical_weight: Mapped[float | None] = mapped_column(Float, nullable=True)
    behavioral_weight: Mapped[float | None] = mapped_column(Float, nullable=True)
    case_study_weight: Mapped[float | None] = mapped_column(Float, nullable=True)
    leadership_weight: Mapped[float | None] = mapped_column(Float, nullable=True)
    communication_weight: Mapped[float | None] = mapped_column(Float, nullable=True)

    # Structured research data
    common_question_types: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    important_competencies: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    interview_stages: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    common_topics: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    reported_question_patterns: Mapped[list | None] = mapped_column(JSONB, nullable=True)

    # Confidence
    research_confidence: Mapped[float | None] = mapped_column(Float, nullable=True)

    def __repr__(self) -> str:
        return f"<OrganizationProfile {self.organization_name} — {self.role}>"
