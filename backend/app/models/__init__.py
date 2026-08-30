"""SQLAlchemy models — import all models here for Alembic auto-detection."""

from app.models.base import Base  # noqa: F401
from app.models.user import User  # noqa: F401
from app.models.candidate import CandidateProfile  # noqa: F401
from app.models.resume import Resume  # noqa: F401
from app.models.job import JobDescription, JobRequirement  # noqa: F401
from app.models.organization import Organization, OrganizationProfile  # noqa: F401
from app.models.interview import (  # noqa: F401
    Interview,
    InterviewPlan,
    InterviewPlanItem,
    InterviewQuestion,
    Answer,
    Evaluation,
)
from app.models.question import (  # noqa: F401
    Competency,
    QuestionIntelligence,
    QuestionObservation,
    QuestionTypeEnum,
    SourceType,
)
from app.models.evaluation import (  # noqa: F401
    EvaluationRubric,
    RubricCriteria,
    CandidateSkillProfile,
    CandidatePerformance,
)

__all__ = [
    "Base",
    "User",
    "CandidateProfile",
    "Resume",
    "JobDescription",
    "JobRequirement",
    "Organization",
    "OrganizationProfile",
    "Interview",
    "InterviewPlan",
    "InterviewPlanItem",
    "InterviewQuestion",
    "Answer",
    "Evaluation",
    "Competency",
    "QuestionIntelligence",
    "QuestionObservation",
    "QuestionTypeEnum",
    "SourceType",
    "EvaluationRubric",
    "RubricCriteria",
    "CandidateSkillProfile",
    "CandidatePerformance",
]
