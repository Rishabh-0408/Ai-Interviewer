"""Report and performance analytics endpoints."""

import uuid
from typing import Any, Dict, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.dependencies import get_current_db_user
from app.interview.engine import interview_engine
from app.models.interview import Interview, InterviewQuestion, Answer, Evaluation
from app.models.user import User

router = APIRouter()


@router.get("", summary="List user reports")
async def list_reports(
    current_user: User = Depends(get_current_db_user),
    db: AsyncSession = Depends(get_db),
) -> List[Dict[str, Any]]:
    """List summary reports for all completed interviews."""
    stmt = (
        select(Interview)
        .where(
            Interview.user_id == current_user.id,
            Interview.overall_score.isnot(None),
        )
        .order_by(Interview.completed_at.desc())
    )
    res = await db.execute(stmt)
    interviews = res.scalars().all()

    return [
        {
            "interview_id": str(i.id),
            "role": i.role,
            "company": i.company,
            "mode": i.mode.value,
            "overall_score": i.overall_score,
            "scores_by_competency": i.scores_by_competency or {},
            "completed_at": i.completed_at.isoformat() if i.completed_at else None,
        }
        for i in interviews
    ]


@router.get("/{interview_id}", summary="Get detailed interview performance report")
async def get_report(
    interview_id: uuid.UUID,
    current_user: User = Depends(get_current_db_user),
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """Retrieve full evaluation scorecard, competency radar, and turn evaluations."""
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

    # If not yet finalized, finalize it now
    if not interview.overall_score and interview.questions:
        await interview_engine.finalize_interview(db, interview)

    turns_data = []
    for q in sorted(interview.questions, key=lambda x: x.order):
        ans = q.answer
        ev = ans.evaluation if ans else None
        turns_data.append({
            "order": q.order,
            "question_text": q.question_text,
            "question_type": q.question_type,
            "competencies": q.competencies or [],
            "is_followup": q.parent_question_id is not None,
            "answer_text": ans.answer_text if ans else None,
            "duration_seconds": ans.duration_seconds if ans else 0,
            "score": ev.score if ev else 0,
            "feedback": ev.feedback if ev else "No feedback",
            "strengths": ev.strengths if ev else [],
            "weaknesses": ev.weaknesses if ev else [],
            "criteria_scores": ev.criteria_scores if ev else {},
        })

    # Prepare radar chart items
    competency_chart = [
        {"competency": comp, "score": score, "fullMark": 100}
        for comp, score in (interview.scores_by_competency or {}).items()
    ]

    return {
        "interview_id": str(interview.id),
        "role": interview.role,
        "company": interview.company,
        "experience_level": interview.experience_level,
        "mode": interview.mode.value,
        "overall_score": interview.overall_score or 75.0,
        "scores_by_competency": interview.scores_by_competency or {},
        "competency_chart": competency_chart,
        "completed_at": interview.completed_at.isoformat() if interview.completed_at else None,
        "duration_minutes": interview.duration_minutes,
        "turns": turns_data,
    }
