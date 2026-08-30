"""Interview planning service for Practice and Simulation modes."""

from typing import List, Dict, Any, Optional
import structlog

logger = structlog.get_logger(__name__)


class InterviewPlanner:
    """Creates structured, timed blueprints for interview sessions."""

    SIMULATION_STAGE_TEMPLATES = {
        "engineering": [
            {"question_type": "rapid_fire_icebreaker", "competency": "Introduction & Background", "weight": 0.1},
            {"question_type": "technical", "competency": "Core Architecture & Data Structures", "weight": 0.3},
            {"question_type": "technical", "competency": "System Design & Scalability", "weight": 0.25},
            {"question_type": "behavioral", "competency": "Team Collaboration & Conflict", "weight": 0.2},
            {"question_type": "situational", "competency": "Engineering Leadership & Priorities", "weight": 0.15},
        ],
        "product": [
            {"question_type": "rapid_fire_icebreaker", "competency": "Introduction & PM Philosophy", "weight": 0.1},
            {"question_type": "case_study", "competency": "Product Sense & Design", "weight": 0.3},
            {"question_type": "analytical", "competency": "Metrics & Execution", "weight": 0.25},
            {"question_type": "behavioral", "competency": "Stakeholder Management", "weight": 0.2},
            {"question_type": "leadership_teamwork", "competency": "Strategic Vision", "weight": 0.15},
        ],
        "general": [
            {"question_type": "personal_motivational", "competency": "Career Goals & Role Alignment", "weight": 0.15},
            {"question_type": "technical", "competency": "Domain Expertise & Problem Solving", "weight": 0.35},
            {"question_type": "behavioral", "competency": "Past Impact & Accountability", "weight": 0.25},
            {"question_type": "situational", "competency": "Ambiguity & Critical Thinking", "weight": 0.25},
        ],
    }

    def build_practice_plan(
        self,
        selected_question_types: List[str],
        duration_minutes: int = 20,
    ) -> List[Dict[str, Any]]:
        """Build an interview plan for Focused Practice mode."""
        if not selected_question_types:
            selected_question_types = ["technical"]

        num_types = len(selected_question_types)
        minutes_per_type = max(3, duration_minutes // num_types)

        items = []
        for i, q_type in enumerate(selected_question_types):
            items.append({
                "order": i + 1,
                "question_type": q_type,
                "competency": q_type.replace("_", " ").title(),
                "allocated_minutes": minutes_per_type,
            })
        return items

    def build_simulation_plan(
        self,
        role: str,
        duration_minutes: int = 30,
    ) -> List[Dict[str, Any]]:
        """Build an interview plan for Real Interview Simulation mode."""
        role_lower = (role or "").lower()
        if any(term in role_lower for term in ["engineer", "developer", "architect", "backend", "frontend", "devops", "sre"]):
            template = self.SIMULATION_STAGE_TEMPLATES["engineering"]
        elif any(term in role_lower for term in ["product", "pm", "program"]):
            template = self.SIMULATION_STAGE_TEMPLATES["product"]
        else:
            template = self.SIMULATION_STAGE_TEMPLATES["general"]

        items = []
        for i, stage in enumerate(template):
            alloc = max(3, int(duration_minutes * stage["weight"]))
            items.append({
                "order": i + 1,
                "question_type": stage["question_type"],
                "competency": stage["competency"],
                "allocated_minutes": alloc,
            })
        return items


# Singleton instance
interview_planner = InterviewPlanner()
