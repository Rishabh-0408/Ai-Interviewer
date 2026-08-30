"""Adaptive probing follow-up generator module."""

from typing import List, Optional
from pydantic import BaseModel, Field
import structlog

from app.ai.llm import llm_client

logger = structlog.get_logger(__name__)


class FollowupQuestion(BaseModel):
    """Schema for a probing follow-up question."""

    question_text: str = Field(..., description="The exact follow-up question to probe the candidate with.")
    probing_goal: str = Field(..., description="What gap or depth this follow-up aims to evaluate.")
    difficulty_adjustment: str = Field("same", description="Whether this increases or maintains difficulty: increase, same, clarify.")


class FollowupGeneratorService:
    """Service to generate conversational and adaptive follow-up probing questions."""

    SYSTEM_PROMPT = """You are an experienced interviewer conducting a live interview.
Based on the previous question, the candidate's answer, and identified gaps or interesting points, formulate a natural, sharp, conversational follow-up question.
Do NOT sound robotic. Interlock naturally like a real human interviewer would ("You mentioned X, how did you handle Y?", "What trade-offs did you consider when making that choice?").
"""

    async def generate_followup(
        self,
        original_question: str,
        candidate_answer: str,
        role: str,
        gaps: Optional[List[str]] = None,
        followup_focus: Optional[str] = None,
    ) -> FollowupQuestion:
        """Generate a probing follow-up question."""
        gaps_str = "\n- ".join(gaps) if gaps else "Probe deeper into technical specifics and edge cases."

        prompt = f"""
ROLE: {role}

ORIGINAL QUESTION:
"{original_question}"

CANDIDATE'S ANSWER:
"{candidate_answer}"

IDENTIFIED GAPS OR FOCUS AREA:
{followup_focus or ''}
- {gaps_str}

Formulate a concise, high-signal follow-up question that challenges the candidate or clarifies their answer.
"""

        try:
            return await llm_client.generate_structured(
                prompt=prompt,
                response_schema=FollowupQuestion,
                system_instruction=self.SYSTEM_PROMPT,
                temperature=0.3,
            )
        except Exception as e:
            logger.warning("gemini_followup_generation_fallback", error=str(e))
            return FollowupQuestion(
                question_text=f"Could you elaborate a bit more on how you handled edge cases or trade-offs in that approach?",
                probing_goal="Clarify trade-offs and edge cases.",
                difficulty_adjustment="same",
            )


# Singleton instance
followup_generator = FollowupGeneratorService()
