"""Interview management and turn-by-turn orchestration endpoints."""

import uuid
from typing import Any, Dict, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.dependencies import get_current_db_user
from app.interview.engine import interview_engine
from app.models.interview import Interview, InterviewQuestion, Answer, Evaluation
from app.models.user import User
from app.schemas.interview import (
    CreateInterviewRequest,
    InterviewDetailResponse,
    QuestionDetail,
    SubmitAnswerRequest,
)

router = APIRouter()


@router.get("", summary="List user interviews")
async def list_interviews(
    current_user: User = Depends(get_current_db_user),
    db: AsyncSession = Depends(get_db),
) -> List[Dict[str, Any]]:
    """List all interview sessions for current user."""
    stmt = (
        select(Interview)
        .where(Interview.user_id == current_user.id)
        .order_by(Interview.created_at.desc())
    )
    result = await db.execute(stmt)
    interviews = result.scalars().all()

    return [
        {
            "id": str(i.id),
            "mode": i.mode.value,
            "status": i.status.value,
            "role": i.role,
            "company": i.company,
            "experience_level": i.experience_level,
            "duration_minutes": i.duration_minutes,
            "overall_score": i.overall_score,
            "created_at": i.created_at.isoformat(),
            "completed_at": i.completed_at.isoformat() if i.completed_at else None,
        }
        for i in interviews
    ]


@router.post("", summary="Create new interview session", status_code=status.HTTP_201_CREATED)
async def create_interview(
    request: CreateInterviewRequest,
    current_user: User = Depends(get_current_db_user),
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """Create a new practice or simulation interview."""
    interview = await interview_engine.create_interview(
        db=db,
        user_id=current_user.id,
        mode=request.mode,
        role=request.role,
        company=request.company,
        experience_level=request.experience_level,
        job_description_id=request.job_description_id,
        resume_id=request.resume_id,
        duration_minutes=request.duration_minutes,
        selected_question_types=request.selected_question_types,
    )
    return {
        "id": str(interview.id),
        "mode": interview.mode.value,
        "status": interview.status.value,
        "role": interview.role,
        "company": interview.company,
        "duration_minutes": interview.duration_minutes,
    }


@router.get("/{interview_id}", summary="Get interview details and turns")
async def get_interview(
    interview_id: uuid.UUID,
    current_user: User = Depends(get_current_db_user),
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """Retrieve full interview details including questions, answers, and evaluations."""
    stmt = (
        select(Interview)
        .where(Interview.id == interview_id, Interview.user_id == current_user.id)
        .options(
            selectinload(Interview.questions)
            .selectinload(InterviewQuestion.answer)
            .selectinload(Answer.evaluation),
            selectinload(Interview.plan),
        )
    )
    res = await db.execute(stmt)
    interview = res.scalar_one_or_none()
    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found")

    questions_data = []
    for q in sorted(interview.questions, key=lambda x: x.order):
        ans = q.answer
        ev = ans.evaluation if ans else None
        questions_data.append({
            "id": str(q.id),
            "order": q.order,
            "question_text": q.question_text,
            "question_type": q.question_type,
            "competencies": q.competencies or [],
            "is_followup": q.parent_question_id is not None,
            "answer_text": ans.answer_text if ans else None,
            "score": ev.score if ev else None,
            "feedback": ev.feedback if ev else None,
            "strengths": ev.strengths if ev else [],
            "weaknesses": ev.weaknesses if ev else [],
        })

    return {
        "id": str(interview.id),
        "mode": interview.mode.value,
        "status": interview.status.value,
        "role": interview.role,
        "company": interview.company,
        "experience_level": interview.experience_level,
        "duration_minutes": interview.duration_minutes,
        "overall_score": interview.overall_score,
        "scores_by_competency": interview.scores_by_competency or {},
        "created_at": interview.created_at.isoformat(),
        "started_at": interview.started_at.isoformat() if interview.started_at else None,
        "completed_at": interview.completed_at.isoformat() if interview.completed_at else None,
        "questions": questions_data,
    }


@router.post("/{interview_id}/start", summary="Start interview")
async def start_interview(
    interview_id: uuid.UUID,
    current_user: User = Depends(get_current_db_user),
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """Start the interview and receive the opening question."""
    try:
        return await interview_engine.start_interview(
            db=db,
            interview_id=interview_id,
            user_id=current_user.id,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{interview_id}/answer", summary="Submit candidate answer")
async def submit_answer(
    interview_id: uuid.UUID,
    request: SubmitAnswerRequest,
    current_user: User = Depends(get_current_db_user),
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """Submit answer to active question, evaluate it, and obtain next question or follow-up."""
    try:
        return await interview_engine.submit_answer(
            db=db,
            interview_id=interview_id,
            question_id=request.question_id,
            answer_text=request.answer_text,
            duration_seconds=request.duration_seconds,
            user_id=current_user.id,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{interview_id}/complete", summary="Complete interview and generate report")
async def complete_interview(
    interview_id: uuid.UUID,
    current_user: User = Depends(get_current_db_user),
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """Finalize the interview early and generate full scorecard."""
    stmt = (
        select(Interview)
        .where(Interview.id == interview_id, Interview.user_id == current_user.id)
        .options(
            selectinload(Interview.questions)
            .selectinload(InterviewQuestion.answer)
            .selectinload(Answer.evaluation),
        )
    )
    res = await db.execute(stmt)
    interview = res.scalar_one_or_none()
    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found")

    report = await interview_engine.finalize_interview(db, interview)
    return {
        "status": "completed",
        "overall_score": interview.overall_score,
        "report": report.model_dump() if hasattr(report, "model_dump") else report,
    }
