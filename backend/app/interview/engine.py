"""Core Interview Engine & State Machine."""

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
import structlog

from app.ai.question_generator import question_generator
from app.ai.answer_evaluator import answer_evaluator
from app.ai.followup_generator import followup_generator
from app.ai.report_generator import report_generator
from app.interview.planner import interview_planner
from app.models.interview import (
    Interview,
    InterviewMode,
    InterviewPlan,
    InterviewPlanItem,
    InterviewQuestion,
    Answer,
    Evaluation,
    InterviewStatus,
)
from app.models.resume import Resume
from app.models.job import JobDescription

logger = structlog.get_logger(__name__)


class InterviewEngine:
    """Orchestrates interview sessions, state transitions, question generation, and evaluations."""

    async def create_interview(
        self,
        db: AsyncSession,
        user_id: uuid.UUID,
        mode: InterviewMode,
        role: str,
        company: Optional[str] = None,
        experience_level: Optional[str] = "mid",
        job_description_id: Optional[uuid.UUID] = None,
        resume_id: Optional[uuid.UUID] = None,
        duration_minutes: int = 20,
        selected_question_types: Optional[List[str]] = None,
    ) -> Interview:
        """Create and plan a new interview session."""
        interview = Interview(
            user_id=user_id,
            mode=mode,
            status=InterviewStatus.PLANNED,
            role=role,
            company=company,
            experience_level=experience_level,
            job_description_id=job_description_id,
            resume_id=resume_id,
            duration_minutes=duration_minutes,
            selected_question_types=selected_question_types or [],
        )
        db.add(interview)
        await db.flush()

        # Build plan
        if mode == InterviewMode.PRACTICE:
            items_data = interview_planner.build_practice_plan(
                selected_question_types=selected_question_types or ["technical"],
                duration_minutes=duration_minutes,
            )
        else:
            items_data = interview_planner.build_simulation_plan(
                role=role,
                duration_minutes=duration_minutes,
            )

        plan = InterviewPlan(
            interview_id=interview.id,
            plan_data={"total_stages": len(items_data), "duration_minutes": duration_minutes},
        )
        db.add(plan)
        await db.flush()

        for item_data in items_data:
            plan_item = InterviewPlanItem(
                plan_id=plan.id,
                order=item_data["order"],
                question_type=item_data["question_type"],
                competency=item_data["competency"],
                allocated_minutes=item_data["allocated_minutes"],
                is_completed=False,
            )
            db.add(plan_item)

        await db.commit()
        await db.refresh(interview)
        return interview

    async def start_interview(
        self,
        db: AsyncSession,
        interview_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> Dict[str, Any]:
        """Start the interview and generate the first question."""
        interview = await self._get_interview_with_relations(db, interview_id, user_id)
        if not interview:
            raise ValueError("Interview not found or unauthorized.")

        interview.status = InterviewStatus.IN_PROGRESS
        interview.started_at = datetime.now(timezone.utc)

        # Context loading
        resume_text, jd_text = await self._get_context_texts(db, interview)

        # First stage item
        plan_items = sorted(interview.plan.items, key=lambda x: x.order) if interview.plan else []
        first_stage = plan_items[0] if plan_items else None

        q_type = first_stage.question_type if first_stage else "technical"
        competency = first_stage.competency if first_stage else "Domain Knowledge"

        gen_q = await question_generator.generate_question(
            role=interview.role or "Software Engineer",
            company=interview.company,
            job_description=jd_text,
            resume_text=resume_text,
            experience_level=interview.experience_level or "mid",
            question_type=q_type,
            target_competency=competency,
        )

        question = InterviewQuestion(
            interview_id=interview.id,
            question_text=gen_q.question_text,
            question_type=gen_q.question_type,
            competencies=gen_q.target_competencies,
            difficulty=2,
            order=1,
            source_type="ai_generated",
            selection_reason=gen_q.context_reasoning,
            confidence=0.95,
        )
        db.add(question)
        await db.commit()
        await db.refresh(question)

        return {
            "interview_id": str(interview.id),
            "status": interview.status.value,
            "question": {
                "id": str(question.id),
                "order": question.order,
                "question_text": question.question_text,
                "question_type": question.question_type,
                "competencies": question.competencies,
                "context_reasoning": question.selection_reason,
            },
            "current_stage": {
                "order": first_stage.order if first_stage else 1,
                "total_stages": len(plan_items),
                "competency": competency,
            },
        }

    async def submit_answer(
        self,
        db: AsyncSession,
        interview_id: uuid.UUID,
        question_id: uuid.UUID,
        answer_text: str,
        duration_seconds: Optional[int] = None,
        user_id: Optional[uuid.UUID] = None,
    ) -> Dict[str, Any]:
        """Submit candidate answer, evaluate it, and determine the next step."""
        interview = await self._get_interview_with_relations(db, interview_id, user_id)
        if not interview:
            raise ValueError("Interview not found or unauthorized.")

        # Find question
        stmt = select(InterviewQuestion).where(
            InterviewQuestion.id == question_id,
            InterviewQuestion.interview_id == interview_id,
        )
        res = await db.execute(stmt)
        question = res.scalar_one_or_none()
        if not question:
            raise ValueError("Question not found.")

        # Save Answer
        answer = Answer(
            question_id=question.id,
            answer_text=answer_text,
            duration_seconds=duration_seconds or 0,
        )
        db.add(answer)
        await db.flush()

        # Evaluate Answer
        evaluation_res = await answer_evaluator.evaluate_answer(
            question_text=question.question_text,
            question_type=question.question_type,
            candidate_answer=answer_text,
            role=interview.role or "Engineer",
            experience_level=interview.experience_level or "mid",
        )

        evaluation = Evaluation(
            answer_id=answer.id,
            score=evaluation_res.score,
            max_score=100.0,
            feedback=evaluation_res.actionable_feedback,
            strengths=evaluation_res.strengths,
            weaknesses=evaluation_res.gaps,
            criteria_scores=evaluation_res.rubric_scores,
            follow_up_reason=evaluation_res.followup_focus if evaluation_res.should_followup else None,
        )
        db.add(evaluation)
        await db.flush()

        # Check follow-up condition
        prior_followups = [q for q in interview.questions if q.parent_question_id == question.id]
        should_probe = evaluation_res.should_followup and len(prior_followups) < 1

        resume_text, jd_text = await self._get_context_texts(db, interview)

        if should_probe:
            followup = await followup_generator.generate_followup(
                original_question=question.question_text,
                candidate_answer=answer_text,
                role=interview.role or "Engineer",
                gaps=evaluation_res.gaps,
                followup_focus=evaluation_res.followup_focus,
            )

            next_q = InterviewQuestion(
                interview_id=interview.id,
                parent_question_id=question.id,
                question_text=followup.question_text,
                question_type="follow_up_probing",
                competencies=question.competencies,
                order=len(interview.questions) + 1,
                source_type="adaptive_followup",
                selection_reason=followup.probing_goal,
                confidence=0.9,
            )
            db.add(next_q)
            await db.commit()
            await db.refresh(next_q)

            return {
                "action": "followup",
                "evaluation": {
                    "score": evaluation.score,
                    "feedback": evaluation.feedback,
                    "strengths": evaluation.strengths,
                    "gaps": evaluation.weaknesses,
                },
                "next_question": {
                    "id": str(next_q.id),
                    "order": next_q.order,
                    "question_text": next_q.question_text,
                    "question_type": next_q.question_type,
                    "is_followup": True,
                    "probing_goal": followup.probing_goal,
                },
            }

        # Otherwise advance to next plan item
        plan_items = sorted(interview.plan.items, key=lambda x: x.order) if interview.plan else []
        next_stage: Optional[InterviewPlanItem] = None
        for item in plan_items:
            if not item.is_completed:
                item.is_completed = True
                continue
            if item.is_completed and next_stage is None and not item.is_completed:
                next_stage = item

        # Find first uncompleted stage
        for item in plan_items:
            if not item.is_completed:
                next_stage = item
                break

        if next_stage:
            gen_q = await question_generator.generate_question(
                role=interview.role or "Engineer",
                company=interview.company,
                job_description=jd_text,
                resume_text=resume_text,
                experience_level=interview.experience_level or "mid",
                question_type=next_stage.question_type,
                target_competency=next_stage.competency,
                previous_questions=[q.question_text for q in interview.questions],
            )

            next_q = InterviewQuestion(
                interview_id=interview.id,
                question_text=gen_q.question_text,
                question_type=gen_q.question_type,
                competencies=gen_q.target_competencies,
                order=len(interview.questions) + 1,
                source_type="ai_generated",
                selection_reason=gen_q.context_reasoning,
                confidence=0.95,
            )
            db.add(next_q)
            await db.commit()
            await db.refresh(next_q)

            return {
                "action": "next_question",
                "evaluation": {
                    "score": evaluation.score,
                    "feedback": evaluation.feedback,
                    "strengths": evaluation.strengths,
                    "gaps": evaluation.weaknesses,
                },
                "next_question": {
                    "id": str(next_q.id),
                    "order": next_q.order,
                    "question_text": next_q.question_text,
                    "question_type": next_q.question_type,
                    "competencies": next_q.competencies,
                    "is_followup": False,
                },
                "stage": {
                    "order": next_stage.order,
                    "total_stages": len(plan_items),
                    "competency": next_stage.competency,
                },
            }

        # If no more stages, complete interview
        report = await self.finalize_interview(db, interview)
        return {
            "action": "completed",
            "evaluation": {
                "score": evaluation.score,
                "feedback": evaluation.feedback,
            },
            "report": report.model_dump(),
        }

    async def finalize_interview(
        self,
        db: AsyncSession,
        interview: Interview,
    ) -> Any:
        """Finalize interview, calculate score breakdown and generate report."""
        interview.status = InterviewStatus.COMPLETED
        interview.completed_at = datetime.now(timezone.utc)

        # Collect turns for report
        turns_data = []
        scores_by_comp: Dict[str, List[float]] = {}

        for q in interview.questions:
            if q.answer and q.answer.evaluation:
                ev = q.answer.evaluation
                turns_data.append({
                    "question_text": q.question_text,
                    "question_type": q.question_type,
                    "candidate_answer": q.answer.answer_text,
                    "score": ev.score,
                    "strengths": ev.strengths or [],
                    "gaps": ev.weaknesses or [],
                    "feedback": ev.feedback,
                })
                # Aggregate competencies
                for comp in (q.competencies or ["General"]):
                    scores_by_comp.setdefault(comp, []).append(ev.score)

        report = await report_generator.generate_report(
            role=interview.role or "Candidate",
            company=interview.company,
            experience_level=interview.experience_level or "mid",
            turns=turns_data,
        )

        interview.overall_score = report.overall_score
        interview.scores_by_competency = {
            c.competency: c.score for c in report.competency_breakdown
        }

        await db.commit()
        return report

    async def _get_interview_with_relations(
        self,
        db: AsyncSession,
        interview_id: uuid.UUID,
        user_id: Optional[uuid.UUID] = None,
    ) -> Optional[Interview]:
        stmt = (
            select(Interview)
            .where(Interview.id == interview_id)
            .options(
                selectinload(Interview.plan).selectinload(InterviewPlan.items),
                selectinload(Interview.questions)
                .selectinload(InterviewQuestion.answer)
                .selectinload(Answer.evaluation),
            )
        )
        if user_id:
            stmt = stmt.where(Interview.user_id == user_id)
        res = await db.execute(stmt)
        return res.scalar_one_or_none()

    async def _get_context_texts(self, db: AsyncSession, interview: Interview) -> tuple[Optional[str], Optional[str]]:
        resume_text = None
        jd_text = None

        if interview.resume_id:
            r_stmt = select(Resume).where(Resume.id == interview.resume_id)
            r_res = await db.execute(r_stmt)
            resume = r_res.scalar_one_or_none()
            if resume:
                resume_text = resume.extracted_text

        if interview.job_description_id:
            j_stmt = select(JobDescription).where(JobDescription.id == interview.job_description_id)
            j_res = await db.execute(j_stmt)
            jd = j_res.scalar_one_or_none()
            if jd:
                jd_text = jd.raw_text

        return resume_text, jd_text


# Singleton instance
interview_engine = InterviewEngine()
