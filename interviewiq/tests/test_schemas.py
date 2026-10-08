from schemas.models import EvaluationResult, QuestionGeneration

def test_evaluation_schema():
    data = {
        "score_overall": 8,
        "technical_accuracy": 7,
        "clarity": 9,
        "depth": 8,
        "communication": 9,
        "relevance": 8,
        "strengths": ["Clear communication"],
        "weaknesses": ["Missed some details"],
        "missing_points": ["Detail A"],
        "ideal_answer": "Complete answer",
        "star_method_used": True
    }
    obj = EvaluationResult(**data)
    assert obj.score_overall == 8

def test_question_schema():
    data = {
        "question": "What is polymorphism?",
        "expected_focus": "Explanation and examples."
    }
    obj = QuestionGeneration(**data)
    assert "polymorphism" in obj.question
