from langchain_core.output_parsers import PydanticOutputParser
from config import get_llm
from prompts.templates import SKILL_GAP_PROMPT
from schemas.models import SkillGapResult

def analyze_skill_gaps(transcript: str) -> SkillGapResult:
    llm = get_llm()
    parser = PydanticOutputParser(pydantic_object=SkillGapResult)
    
    try:
        chain = SKILL_GAP_PROMPT | llm.with_structured_output(SkillGapResult)
        return chain.invoke({"transcript": transcript})
    except Exception:
        chain = SKILL_GAP_PROMPT | llm
        prompt_val = SKILL_GAP_PROMPT.format_messages(transcript=transcript)
        prompt_val[0].content += f"\n\n{parser.get_format_instructions()}"
        res = llm.invoke(prompt_val)
        try:
            return parser.parse(res.content)
        except Exception:
            return SkillGapResult(
                categories={"General": 50},
                top_strengths=["Communication"],
                top_gaps=["Technical Depth"],
                readiness_level="Needs Work"
            )
