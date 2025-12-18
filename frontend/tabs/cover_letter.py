import streamlit as st
from frontend import ui
from agents import ResumeAnalysisAgent


def generate_cover_letter(agent: ResumeAnalysisAgent, company: str, role: str, jd: str, tone: str, length: str):
    try:
        with st.spinner("Generating cover letter..."):
            return agent.generate_cover_letter(company=company, role=role, job_description=jd, tone=tone, length=length)
    except Exception as e:
        st.error(f"Error generating cover letter: {e}")
        return "Error generating cover letter."


def render(agent):
    if st.session_state.resume_analyzed and agent:
        ui.cover_letter_section(
            has_resume=True,
            generate_cover_letter_func=lambda company, role, jd, tone, length: generate_cover_letter(
                agent, company, role, jd, tone, length
            ),
        )
    else:
        st.warning("Please upload and analyze a resume first in the 'Resume Analysis' tab.")
