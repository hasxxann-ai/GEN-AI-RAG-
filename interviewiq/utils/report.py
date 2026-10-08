def generate_markdown_report(session_state) -> str:
    if not session_state.study_plan_result:
        return "No study plan available."
        
    plan = session_state.study_plan_result
    
    md = f"# Improvement Plan for {session_state.role}\n\n"
    md += f"**Duration:** {plan.get('duration_days', 7)} days\n\n"
    
    md += "## Daily Plan\n"
    for day in plan.get('daily_plan', []):
        md += f"### Day {day.get('day')}\n"
        md += f"**Goals:** {', '.join(day.get('goals', []))}\n"
        md += f"**Topics:** {', '.join(day.get('topics', []))}\n"
        md += f"**Tasks:** {', '.join(day.get('practice_tasks', []))}\n"
        md += f"**Resources:** {', '.join(day.get('resources', []))}\n\n"
        
    md += "## Practice Questions\n"
    for category, qs in plan.get('practice_questions', {}).items():
        md += f"### {category}\n"
        for q in qs:
            md += f"- {q}\n"
            
    md += "\n## Communication Tips\n"
    for tip in plan.get('communication_tips', []):
        md += f"- {tip}\n"
        
    return md
