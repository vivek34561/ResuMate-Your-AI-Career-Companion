import streamlit as st
from frontend import ui
from agents import ResumeAnalysisAgent


def improve_resume(_client_unused, improvement_areas: list, target_role: str):
    try:
        agent: ResumeAnalysisAgent = st.session_state.get("resume_agent")
        if not agent:
            st.error("Agent not initialized. Configure provider/API key in sidebar.")
            return {}
        with st.spinner("Generating improvement suggestions..."):
            return agent.improve_resume(improvement_areas or [], target_role)
    except Exception as e:
        st.error(f"Error generating improvement suggestions: {e}")
        return {}


def get_improved_resume(_client_unused, target_role: str, highlight_skills: str):
    try:
        agent: ResumeAnalysisAgent = st.session_state.get("resume_agent")
        if not agent:
            return "Agent not initialized. Configure provider/API key in sidebar."
        with st.spinner("Generating improved resume..."):
            return agent.get_improved_resume(target_role=target_role, highlight_skills=highlight_skills)
    except Exception:
        return "Error generating improved resume."


def render(client=None):
    if st.session_state.resume_analyzed:
        ui.resume_improvement_section(
            has_resume=True,
            improve_resume_func=lambda areas, role: improve_resume(None, areas, role),
            get_improved_resume_func=lambda role, skills: get_improved_resume(None, role, skills),
        )
    else:
        st.warning("Please upload and analyze a resume first in the 'Resume Analysis' tab.")
