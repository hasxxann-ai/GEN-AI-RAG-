from langchain_core.tools import tool
from agents.question_agent import generate_question
from agents.evaluator_agent import evaluate_answer
from agents.skill_gap_agent import analyze_skill_gaps
from agents.coach_agent import build_study_plan
from pypdf import PdfReader
import io

@tool
def generate_question_tool(role: str, level: str, interview_type: str, difficulty: str, resume_context: str, history: str, q_num: int) -> str:
    """Tool to generate the next interview question."""
    res = generate_question(role, level, interview_type, difficulty, resume_context, history, q_num)
    return res.json()

@tool
def evaluate_answer_tool(question: str, answer: str) -> str:
    """Tool to evaluate a candidate's answer."""
    res = evaluate_answer(question, answer)
    return res.json()

@tool
def analyze_skill_gaps_tool(transcript: str) -> str:
    """Tool to analyze skill gaps from an interview transcript."""
    res = analyze_skill_gaps(transcript)
    return res.json()

@tool
def build_study_plan_tool(role: str, skill_gaps: str, duration: int) -> str:
    """Tool to build a study plan based on skill gaps."""
    res = build_study_plan(role, skill_gaps, duration)
    return res.json()

@tool
def resume_parser_tool(pdf_path_or_text: str, is_pdf: bool = False) -> str:
    """Extracts text from a resume PDF or returns text."""
    if not is_pdf:
        return pdf_path_or_text
    
    try:
        reader = PdfReader(pdf_path_or_text)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        return text[:3000] # truncate to avoid huge contexts
    except Exception as e:
        return f"Could not parse resume: {str(e)}"
