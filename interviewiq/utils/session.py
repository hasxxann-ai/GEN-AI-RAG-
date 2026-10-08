from pydantic import BaseModel
from typing import List, Optional, Dict
from schemas.models import EvaluationResult

class QA_Pair(BaseModel):
    question: str
    expected_focus: str
    answer: Optional[str] = None
    evaluation: Optional[EvaluationResult] = None

class SessionState(BaseModel):
    role: str = ""
    level: str = ""
    interview_type: str = ""
    difficulty: str = ""
    resume_context: str = ""
    target_questions: int = 5
    current_q_index: int = 0
    history: List[QA_Pair] = []
    
    skill_gap_result: Optional[dict] = None
    study_plan_result: Optional[dict] = None
    agent_trace: List[str] = []

    def get_transcript(self) -> str:
        transcript = ""
        for i, pair in enumerate(self.history):
            transcript += f"Q{i+1}: {pair.question}\n"
            transcript += f"A{i+1}: {pair.answer}\n"
            if pair.evaluation:
                transcript += f"Score: {pair.evaluation.score_overall}/10\n"
            transcript += "---\n"
        return transcript
