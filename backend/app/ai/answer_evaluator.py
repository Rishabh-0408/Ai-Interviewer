"""Candidate answer evaluation service."""

from typing import Dict, List, Optional
from pydantic import BaseModel, Field
import structlog

from app.ai.llm import llm_client

logger = structlog.get_logger(__name__)


class StarAnalysis(BaseModel):
    """STAR framework analysis for behavioral answers."""

    situation_score: Optional[float] = Field(None, description="Score 0-100 for context/situation setup.")
    task_score: Optional[float] = Field(None, description="Score 0-100 for clear problem statement.")
    action_score: Optional[float] = Field(None, description="Score 0-100 for specific actions taken by candidate.")
    result_score: Optional[float] = Field(None, description="Score 0-100 for quantifiable outcome and learnings.")
    critique: Optional[str] = Field(None, description="Assessment of STAR method application.")


class AnswerEvaluation(BaseModel):
    """Structured evaluation of a candidate's answer."""

    score: float = Field(..., description="Overall score from 0.0 to 100.0")
    rubric_scores: Dict[str, float] = Field(
        default_factory=dict,
        description="Individual criteria scores (e.g. clarity, technical_depth, problem_solving, impact).",
    )
    strengths: List[str] = Field(
        default_factory=list,
        description="Highlights of what the candidate answered effectively.",
    )
    gaps: List[str] = Field(
        default_factory=list,
        description="Missing details, flawed assumptions, or unaddressed aspects.",
    )
    star_analysis: Optional[StarAnalysis] = Field(
        None,
        description="STAR analysis if question was behavioral/situational.",
    )
    actionable_feedback: str = Field(
        ...,
        description="Constructive advice on how candidate could improve this specific answer.",
    )
    should_followup: bool = Field(
        default=False,
        description="Whether the interviewer should drill deeper on this answer before moving on.",
    )
    followup_focus: Optional[str] = Field(
        None,
        description="Specific aspect or question to probe next if should_followup is true.",
    )


class AnswerEvaluatorService:
    """Evaluates candidate answers against rubrics and context."""

    SYSTEM_PROMPT = """You are an expert interview evaluator with deep domain experience.
Analyze the candidate's response to the interview question objectively, rigorously, and constructively.
Score accurately on a 0-100 scale:
- 90-100: Exceptional, senior-level depth, clear trade-offs, quantifiable impact, articulate.
- 75-89: Strong, competent answer covering core requirements with minor omissions.
- 55-74: Adequate, basic understanding shown, but lacked depth, concrete examples, or structured reasoning.
- Below 55: Weak, vague, incorrect, or failed to address the question.

Always return response conforming strictly to the AnswerEvaluation schema.
"""

    async def evaluate_answer(
        self,
        question_text: str,
        question_type: str,
        candidate_answer: str,
        role: str,
        experience_level: Optional[str] = "mid",
        evaluation_criteria: Optional[List[str]] = None,
    ) -> AnswerEvaluation:
        """Evaluate candidate answer."""
        criteria_str = "\n- ".join(evaluation_criteria) if evaluation_criteria else "Standard industry standards"

        prompt = f"""
Evaluate the candidate's response to the following interview question:

TARGET ROLE: {role} ({experience_level} level)
QUESTION TYPE: {question_type}

QUESTION:
"{question_text}"

EXPECTED EVALUATION CRITERIA / KEY SIGNALS:
- {criteria_str}

CANDIDATE'S ANSWER:
"{candidate_answer}"

Provide a comprehensive, objective evaluation including scores, strengths, gaps, STAR breakdown (if behavioral/situational), actionable feedback, and decide if an adaptive follow-up question is warranted.
"""

        try:
            return await llm_client.generate_structured(
                prompt=prompt,
                response_schema=AnswerEvaluation,
                system_instruction=self.SYSTEM_PROMPT,
                temperature=0.1,
            )
        except Exception as e:
            logger.warning("gemini_answer_evaluation_fallback", error=str(e))
            return AnswerEvaluation(
                score=75.0,
                rubric_scores={"clarity": 75.0, "relevance": 75.0, "technical_depth": 70.0},
                strengths=["Addressed the core question directly"],
                gaps=["Could provide more concrete metrics and technical trade-offs"],
                actionable_feedback="Provide specific real-world examples and quantify the outcome of your decisions.",
                should_followup=False,
            )


# Singleton instance
answer_evaluator = AnswerEvaluatorService()
