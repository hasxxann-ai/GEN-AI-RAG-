import gradio as gr
from utils.session import SessionState, QA_Pair
from agents.question_agent import generate_question
from agents.evaluator_agent import evaluate_answer
from agents.skill_gap_agent import analyze_skill_gaps
from agents.coach_agent import build_study_plan
from tools.tools import resume_parser_tool
from utils.report import generate_markdown_report
import matplotlib.pyplot as plt
import io
from PIL import Image

def build_ui():
    theme = gr.themes.Soft()
    with gr.Blocks(theme=theme, title="InterviewIQ") as demo:
        session_state = gr.State(SessionState().model_dump())
        
        gr.Markdown("# 🚀 InterviewIQ: AI-Powered Interview Preparation")
        
        with gr.Tabs():
            # TAB 1: SETUP
            with gr.Tab("1. Setup"):
                with gr.Row():
                    role = gr.Dropdown(["Software Engineer", "Data Analyst", "ML Engineer", "Product Manager"], allow_custom_value=True, label="Target Role")
                    level = gr.Dropdown(["Fresher", "Junior", "Mid", "Senior"], label="Experience Level")
                with gr.Row():
                    int_type = gr.Dropdown(["Technical", "HR", "Behavioral", "Mixed"], label="Interview Type")
                    difficulty = gr.Dropdown(["Easy", "Medium", "Hard"], label="Difficulty")
                    num_q = gr.Slider(minimum=3, maximum=10, step=1, value=5, label="Number of Questions")
                resume_file = gr.File(label="Upload Resume (PDF) - Optional", file_types=[".pdf"])
                
                start_btn = gr.Button("Start Interview", variant="primary")
                setup_msg = gr.Markdown()
                
            # TAB 2: MOCK INTERVIEW
            with gr.Tab("2. Mock Interview") as mock_tab:
                progress_html = gr.HTML("<b>Progress: 0 / 0</b>")
                chat_history = gr.Chatbot(label="Interview Chat", height=400)
                
                with gr.Row():
                    user_answer = gr.Textbox(lines=3, placeholder="Type your answer here...", label="Your Answer")
                
                with gr.Row():
                    submit_ans_btn = gr.Button("Submit Answer", variant="primary")
                    skip_btn = gr.Button("Skip Question")
                    end_btn = gr.Button("End Interview Early", variant="stop")
                    
                feedback_md = gr.Markdown("### Feedback will appear here after submission.")
                
            # TAB 3: RESULTS
            with gr.Tab("3. Results"):
                results_md = gr.Markdown("Finish the interview to see results.")
                results_plot = gr.Image(label="Skill Radar Chart", type="pil")
                
            # TAB 4: IMPROVEMENT PLAN
            with gr.Tab("4. Improvement Plan"):
                plan_md = gr.Markdown("Finish the interview to get a personalized plan.")
                download_btn = gr.DownloadButton("Download Plan (Markdown)")
                
            # TAB 5: AGENT TRACE
            with gr.Tab("5. Agent Trace"):
                trace_box = gr.Textbox(lines=15, label="Agent Thinking & Tool Calls", interactive=False)

        # INTERACTION LOGIC
        def start_interview(r, l, t, d, n, f_obj, state_dict):
            state = SessionState(**state_dict)
            state.role = r
            state.level = l
            state.interview_type = t
            state.difficulty = d
            state.target_questions = n
            state.history = []
            state.current_q_index = 0
            
            state.agent_trace.append(f"Started session for {r} ({l})")
            
            if f_obj:
                state.agent_trace.append("Called tool: resume_parser_tool")
                state.resume_context = resume_parser_tool.invoke({"pdf_path_or_text": f_obj.name, "is_pdf": True})
            
            # Generate first question
            state.agent_trace.append("Called tool: generate_question_tool")
            q_data = generate_question(state.role, state.level, state.interview_type, state.difficulty, state.resume_context, "", 1)
            
            state.history.append(QA_Pair(question=q_data.question, expected_focus=q_data.expected_focus))
            
            chat = [[None, q_data.question]]
            progress = f"<b>Progress: 1 / {state.target_questions}</b>"
            
            return state.model_dump(), chat, progress, "Interview Started! Go to 'Mock Interview' tab."
            
        start_btn.click(
            start_interview, 
            inputs=[role, level, int_type, difficulty, num_q, resume_file, session_state], 
            outputs=[session_state, chat_history, progress_html, setup_msg]
        )
        
        def process_answer(ans, state_dict, chat):
            state = SessionState(**state_dict)
            if state.current_q_index >= len(state.history):
                return state.model_dump(), chat, "Interview Over", "No active question.", "\n".join(state.agent_trace)
                
            current_q = state.history[state.current_q_index]
            current_q.answer = ans
            chat.append([ans, None]) # Show user answer
            
            # Evaluate
            state.agent_trace.append(f"Called tool: evaluate_answer_tool for Q{state.current_q_index+1}")
            eval_res = evaluate_answer(current_q.question, ans)
            current_q.evaluation = eval_res
            
            feedback = f"**Score:** {eval_res.score_overall}/10\n\n**Strengths:** {', '.join(eval_res.strengths)}\n\n**Weaknesses:** {', '.join(eval_res.weaknesses)}\n\n**Ideal Answer:** {eval_res.ideal_answer}"
            
            state.current_q_index += 1
            
            if state.current_q_index < state.target_questions:
                # Next Question
                state.agent_trace.append("Called tool: generate_question_tool")
                history_text = "\n".join([f"Q: {p.question}\nA: {p.answer}" for p in state.history])
                q_data = generate_question(state.role, state.level, state.interview_type, state.difficulty, state.resume_context, history_text, state.current_q_index + 1)
                state.history.append(QA_Pair(question=q_data.question, expected_focus=q_data.expected_focus))
                chat.append([None, q_data.question])
                progress = f"<b>Progress: {state.current_q_index + 1} / {state.target_questions}</b>"
            else:
                progress = "<b>Progress: Completed! Go to Results tab.</b>"
                chat.append([None, "Interview Complete! Please check your Results and Improvement Plan."])
                
            return state.model_dump(), chat, progress, feedback, "\n".join(state.agent_trace)
            
        submit_ans_btn.click(
            process_answer,
            inputs=[user_answer, session_state, chat_history],
            outputs=[session_state, chat_history, progress_html, feedback_md, trace_box]
        ).then(lambda: "", None, user_answer) # clear text box
        
        def finish_interview(state_dict):
            state = SessionState(**state_dict)
            if not state.history:
                return "No data", None, "No plan", None, "\n".join(state.agent_trace)
                
            transcript = state.get_transcript()
            
            state.agent_trace.append("Called tool: analyze_skill_gaps_tool")
            gaps = analyze_skill_gaps(transcript)
            state.skill_gap_result = gaps.model_dump()
            
            state.agent_trace.append("Called tool: build_study_plan_tool")
            plan = build_study_plan(state.role, str(state.skill_gap_result), 7)
            state.study_plan_result = plan.model_dump()
            
            # Make radar chart
            cats = list(gaps.categories.keys())
            scores = list(gaps.categories.values())
            if cats:
                cats += cats[:1]
                scores += scores[:1]
                
                fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))
                angles = [n / float(len(cats)-1) * 2 * 3.14159 for n in range(len(cats))]
                ax.plot(angles, scores)
                ax.fill(angles, scores, alpha=0.25)
                ax.set_xticks(angles[:-1])
                ax.set_xticklabels(cats[:-1])
                ax.set_ylim(0, 100)
                
                buf = io.BytesIO()
                plt.savefig(buf, format='png')
                buf.seek(0)
                img = Image.open(buf)
            else:
                img = None
                
            res_md = f"### Overall Readiness: {gaps.readiness_level}\n\n**Top Strengths:**\n" + "\n".join([f"- {s}" for s in gaps.top_strengths]) + f"\n\n**Top Gaps:**\n" + "\n".join([f"- {g}" for g in gaps.top_gaps])
            
            md_report = generate_markdown_report(state)
            
            # Save markdown to file for download
            report_path = "improvement_plan.md"
            with open(report_path, "w") as f:
                f.write(md_report)
            
            return res_md, img, md_report, report_path, "\n".join(state.agent_trace)
            
        end_btn.click(
            finish_interview,
            inputs=[session_state],
            outputs=[results_md, results_plot, plan_md, download_btn, trace_box]
        )
            
    return demo
