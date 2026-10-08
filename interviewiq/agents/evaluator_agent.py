from langchain_core.output_parsers import PydanticOutputParser
from config import get_llm
from prompts.templates import EVALUATOR_AGENT_PROMPT
from schemas.models import EvaluationResult

def evaluate_answer(question: str, answer: str) -> EvaluationResult:
    llm = get_llm()
    parser = PydanticOutputParser(pydantic_object=EvaluationResult)
    
    # Check if empty answer
    if not answer or not answer.strip():
        return EvaluationResult(
            score_overall=0, technical_accuracy=0, clarity=0, depth=0, communication=0, relevance=0,
            strengths=[], weaknesses=["Did not provide an answer."], missing_points=["Everything."],
            ideal_answer="A complete answer addressing the core concepts of the question.",
            star_method_used=False
        )
        
    try:
        chain = EVALUATOR_AGENT_PROMPT | llm.with_structured_output(EvaluationResult)
        return chain.invoke({
            "question": question,
            "answer": answer
        })
    except Exception:
        chain = EVALUATOR_AGENT_PROMPT | llm
        prompt_val = EVALUATOR_AGENT_PROMPT.format_messages(question=question, answer=answer)
        prompt_val[0].content += f"\n\n{parser.get_format_instructions()}"
        res = llm.invoke(prompt_val)
        try:
            return parser.parse(res.content)
        except Exception:
            return EvaluationResult(
                score_overall=5, technical_accuracy=5, clarity=5, depth=5, communication=5, relevance=5,
                strengths=["Attempted to answer."], weaknesses=["Could not parse detailed evaluation."],
                missing_points=[], ideal_answer="Ideal answer generation failed.", star_method_used=None
            )
