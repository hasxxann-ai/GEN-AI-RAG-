from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.exceptions import OutputParserException
from config import get_llm
from prompts.templates import QUESTION_AGENT_PROMPT
from schemas.models import QuestionGeneration
import json

def generate_question(role: str, level: str, interview_type: str, difficulty: str, resume_context: str, history: str, q_num: int) -> QuestionGeneration:
    llm = get_llm()
    parser = PydanticOutputParser(pydantic_object=QuestionGeneration)
    
    # Try using native structured output if supported, else fallback to parsing
    try:
        chain = QUESTION_AGENT_PROMPT | llm.with_structured_output(QuestionGeneration)
        return chain.invoke({
            "role": role,
            "level": level,
            "interview_type": interview_type,
            "difficulty": difficulty,
            "resume_context": resume_context,
            "history": history,
            "q_num": q_num
        })
    except Exception:
        # Fallback for models not supporting with_structured_output well
        chain = QUESTION_AGENT_PROMPT | llm
        prompt_val = QUESTION_AGENT_PROMPT.format_messages(
            role=role, level=level, interview_type=interview_type, 
            difficulty=difficulty, resume_context=resume_context, 
            history=history, q_num=q_num
        )
        # Add format instructions manually
        prompt_val[0].content += f"\n\n{parser.get_format_instructions()}"
        res = llm.invoke(prompt_val)
        
        try:
            return parser.parse(res.content)
        except OutputParserException:
            # Basic fallback if parsing fails completely
            return QuestionGeneration(
                question="Could you tell me more about your experience with these technologies?",
                expected_focus="General overview of experience."
            )
