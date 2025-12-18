import streamlit as st
from frontend import ui
from agents import ResumeAnalysisAgent


def improve_resume(agent: ResumeAnalysisAgent, improvement_areas: list, target_role: str):
    try:
        result = agent.improve_resume(improvement_areas, target_role)
        if result:
            has_content = any(
                imp.get('specific') and len(imp.get('specific', [])) > 1
                for imp in result.values() if isinstance(imp, dict)
            )
            if not has_content:
                st.warning("⚠️ Received generic suggestions. The AI may need more context. Try analyzing the resume first or providing a target role.")
        return result
    except Exception as e:
        st.error(f"Error generating improvement suggestions: {e}")
        import traceback
        st.code(traceback.format_exc())
        return {}


def get_improved_resume(agent: ResumeAnalysisAgent, target_role: str, highlight_skills: str):
    try:
        with st.spinner("Generating improved resume..."):
            return agent.get_improved_resume(target_role, highlight_skills)
    except Exception as e:
        st.error(f"Error generating improved resume: {e}")
        return "Error generating improved resume."


def render(agent):
    if st.session_state.resume_analyzed and agent:
        ui.resume_improvement_section(
            has_resume=True,
            improve_resume_func=lambda areas, role: improve_resume(agent, areas, role),
            get_improved_resume_func=lambda role, skills: get_improved_resume(agent, role, skills),
        )
    else:
        st.warning("Please upload and analyze a resume first in the 'Resume Analysis' tab.")
