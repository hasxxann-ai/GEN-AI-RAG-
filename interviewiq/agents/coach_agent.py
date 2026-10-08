from langchain_core.output_parsers import PydanticOutputParser
from config import get_llm
from prompts.templates import COACH_PROMPT
from schemas.models import ImprovementPlan

def build_study_plan(role: str, skill_gaps: str, duration: int = 7) -> ImprovementPlan:
    llm = get_llm()
    parser = PydanticOutputParser(pydantic_object=ImprovementPlan)
    
    try:
        chain = COACH_PROMPT | llm.with_structured_output(ImprovementPlan)
        return chain.invoke({"role": role, "duration": duration, "skill_gaps": skill_gaps})
    except Exception:
        chain = COACH_PROMPT | llm
        prompt_val = COACH_PROMPT.format_messages(role=role, duration=duration, skill_gaps=skill_gaps)
        prompt_val[0].content += f"\n\n{parser.get_format_instructions()}"
        res = llm.invoke(prompt_val)
        try:
            return parser.parse(res.content)
        except Exception:
            return ImprovementPlan(
                duration_days=duration,
                daily_plan=[],
                practice_questions={},
                communication_tips=["Stay calm and structured."]
            )
