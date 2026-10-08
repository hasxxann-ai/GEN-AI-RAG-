from pydantic import BaseModel, Field
from typing import List, Optional, Dict

class EvaluationResult(BaseModel):
    score_overall: int = Field(description="Overall score from 0 to 10")
    technical_accuracy: int = Field(description="Score for technical accuracy (0-10)")
    clarity: int = Field(description="Score for clarity of the answer (0-10)")
    depth: int = Field(description="Score for depth of knowledge (0-10)")
    communication: int = Field(description="Score for communication skills (0-10)")
    relevance: int = Field(description="Score for relevance to the question (0-10)")
    strengths: List[str] = Field(description="List of strengths in the candidate's answer")
    weaknesses: List[str] = Field(description="List of weaknesses or mistakes")
    missing_points: List[str] = Field(description="List of points the candidate missed")
    ideal_answer: str = Field(description="A model/ideal answer to this question")
    star_method_used: Optional[bool] = Field(description="For behavioral questions, whether STAR method was used. True/False or None.")

class SkillGapResult(BaseModel):
    categories: Dict[str, int] = Field(description="Dictionary of skill categories and their scores (0-100)")
    top_strengths: List[str] = Field(description="Top 3 strengths")
    top_gaps: List[str] = Field(description="Top 3 skill gaps")
    readiness_level: str = Field(description="One of: Not Ready, Needs Work, Almost Ready, Interview Ready")

class StudyPlanDay(BaseModel):
    day: int = Field(description="Day number (1 to 14)")
    goals: List[str] = Field(description="Goals for the day")
    topics: List[str] = Field(description="Topics to study")
    practice_tasks: List[str] = Field(description="Practice tasks for the day")
    resources: List[str] = Field(description="Types of resources to use (no fabricated URLs)")

class ImprovementPlan(BaseModel):
    duration_days: int = Field(description="Total duration in days (7 or 14)")
    daily_plan: List[StudyPlanDay] = Field(description="Day-by-day plan")
    practice_questions: Dict[str, List[str]] = Field(description="Practice questions per weak area")
    communication_tips: List[str] = Field(description="Tips for communication and confidence")

class QuestionGeneration(BaseModel):
    question: str = Field(description="The interview question to ask")
    expected_focus: str = Field(description="What the interviewer is looking for in the answer")
