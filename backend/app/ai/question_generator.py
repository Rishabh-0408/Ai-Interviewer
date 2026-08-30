"""Evidence-driven question generation module."""

from typing import List, Optional
from pydantic import BaseModel, Field
import structlog

from app.ai.llm import llm_client
from app.models.question import QuestionTypeEnum

logger = structlog.get_logger(__name__)


class GeneratedQuestion(BaseModel):
    """Schema for a generated interview question."""

    question_text: str = Field(..., description="The exact question to ask the candidate.")
    question_type: str = Field(..., description="The category/type of the question.")
    target_competencies: List[str] = Field(
        default_factory=list,
        description="The competencies or skills evaluated by this question.",
    )
    difficulty: str = Field("medium", description="Question difficulty: junior, mid, senior, lead.")
    evaluation_criteria: List[str] = Field(
        default_factory=list,
        description="Key points a strong candidate answer should touch upon.",
    )
    context_reasoning: str = Field(
        ...,
        description="Why this question is relevant for this candidate, role, company, and stage.",
    )


class QuestionGeneratorService:
    """Service to generate tailored, realistic interview questions."""

    SYSTEM_PROMPT = """You are an elite, highly experienced hiring manager and interview expert conducting an interview.
Your goal is to formulate realistic, rigorous, and personalized interview questions based on the candidate's target role, company, job description, resume, and target question category.
Avoid generic quiz questions. Questions must feel like a real conversational dialogue from a top-tier interviewer.
Always provide the response conforming strictly to the requested schema.
"""

    async def generate_question(
        self,
        role: str,
        company: Optional[str] = None,
        job_description: Optional[str] = None,
        resume_text: Optional[str] = None,
        experience_level: Optional[str] = "mid",
        question_type: str = "technical",
        target_competency: Optional[str] = None,
        previous_questions: Optional[List[str]] = None,
    ) -> GeneratedQuestion:
        """Generate an evidence-driven interview question."""
        prev_q_str = "\n- ".join(previous_questions) if previous_questions else "None (First question)"

        prompt = f"""
Generate an interview question tailored to the following context:

- Target Role: {role}
- Target Company: {company or 'A top tech company in this domain'}
- Experience Level: {experience_level}
- Target Question Category: {question_type}
- Specific Competency to Test: {target_competency or 'Core role competency'}

CANDIDATE RESUME SUMMARY:
{resume_text[:2000] if resume_text else 'Not provided'}

JOB DESCRIPTION / REQUIREMENTS:
{job_description[:2000] if job_description else 'Standard expectations for this role'}

PREVIOUSLY ASKED QUESTIONS IN THIS SESSION (DO NOT REPEAT):
- {prev_q_str}

Please generate a high-signal, natural interview question that directly tests this competency in the context of the role and candidate background.
"""

        try:
            return await llm_client.generate_structured(
                prompt=prompt,
                response_schema=GeneratedQuestion,
                system_instruction=self.SYSTEM_PROMPT,
                temperature=0.4,
            )
        except Exception as e:
            logger.warning("gemini_question_generation_fallback", error=str(e))
            # Fallback safe question
            return GeneratedQuestion(
                question_text=f"Could you walk me through your experience as a {role}, highlighting a recent technical challenge you solved?",
                question_type=question_type,
                target_competencies=[target_competency or "Problem Solving", "Domain Knowledge"],
                difficulty=experience_level or "mid",
                evaluation_criteria=["Clarity", "Depth of technical explanation", "Impact"],
                context_reasoning="Fallback question assessing core domain competence.",
            )


# Singleton instance
question_generator = QuestionGeneratorService()
