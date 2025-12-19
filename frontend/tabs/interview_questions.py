import streamlit as st
from frontend import ui
from agents import ResumeAnalysisAgent


def generate_interview_questions(_client_unused, question_types, difficulty, num_questions):
    try:
        with st.spinner("Generating personalized interview questions..."):
            agent: ResumeAnalysisAgent = st.session_state.get("resume_agent")
            if not agent:
                st.error("Agent not initialized. Configure provider/API key in sidebar.")
                return []
            return agent.generate_interview_questions(question_types, difficulty, num_questions)
    except Exception as e:
        st.error(f"Error Generating questions:{e}")
        return []


def render(client=None):
    if st.session_state.resume_analyzed:
        ui.interview_questions_section(
            has_resume=True,
            generate_questions_func=lambda types, diff, num: generate_interview_questions(None, types, diff, num),
        )
    else:
        st.warning("please upload and analyze a resume first in the 'Resume Analysis' tab.")
