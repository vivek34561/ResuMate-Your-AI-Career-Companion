import streamlit as st
from frontend import ui
from agents import ResumeAnalysisAgent


def ask_question(_client_unused, question, chat_history=None):
    try:
        with st.spinner("Answering using local agent..."):
            agent: ResumeAnalysisAgent = st.session_state.get("resume_agent")
            if not agent:
                return "Agent not initialized. Configure provider/API key in sidebar."
            return agent.ask_question(question, chat_history or [])
    except Exception as e:
        return f"Error: {e}"


def render(client=None):
    if st.session_state.resume_analyzed:
        ui.resume_qa_section(
            has_resume=True,
            ask_question_func=lambda q, h=None: ask_question(None, q, h),
        )
    else:
        st.warning("Please upload and analyze a resume first in the 'Resume Analysis' tab.")
