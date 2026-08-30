"""Pydantic schemas for Interview APIs."""

import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from app.models.interview import InterviewMode, InterviewStatus


class CreateInterviewRequest(BaseModel):
    """Request to create a new interview session."""

    mode: InterviewMode = Field(..., description="Practice or Simulation")
    role: str = Field(..., description="Target role (e.g., 'Senior Backend Engineer')")
    company: Optional[str] = Field(None, description="Target company")
    experience_level: Optional[str] = Field("mid", description="junior, mid, senior, lead")
    job_description_id: Optional[uuid.UUID] = Field(None, description="Linked JD ID")
    resume_id: Optional[uuid.UUID] = Field(None, description="Linked Resume ID")
    duration_minutes: int = Field(20, ge=5, le=120, description="Interview duration")
    selected_question_types: Optional[List[str]] = Field(
        default=None,
        description="For Practice Mode: list of question categories to practice",
    )


class QuestionDetail(BaseModel):
    """Details of a question turn."""

    id: uuid.UUID
    order: int
    question_text: str
    question_type: str
    competencies: Optional[List[str]] = None
    is_followup: bool = False
    answer_text: Optional[str] = None
    score: Optional[float] = None
    feedback: Optional[str] = None


class InterviewDetailResponse(BaseModel):
    """Full detail of an interview session."""

    id: uuid.UUID
    mode: InterviewMode
    status: InterviewStatus
    role: Optional[str] = None
    company: Optional[str] = None
    experience_level: Optional[str] = None
    duration_minutes: Optional[int] = None
    overall_score: Optional[float] = None
    scores_by_competency: Optional[Dict[str, Any]] = None
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    questions: List[QuestionDetail] = []


class SubmitAnswerRequest(BaseModel):
    """Request payload when submitting an answer to a question."""

    question_id: uuid.UUID
    answer_text: str
    duration_seconds: Optional[int] = 0
