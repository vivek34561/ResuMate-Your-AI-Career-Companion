import streamlit as st
from frontend import ui
from frontend.backend_client import BackendClient


def generate_interview_questions(client: BackendClient, question_types, difficulty, num_questions):
    try:
        with st.spinner("Generating personalized interview questions via backend..."):
            resume_id = st.session_state.get("active_resume_id") or st.session_state.get("use_saved_resume_id") or st.session_state.get("selected_resume_id")
            questions = client.generate_interview_questions(
                user=st.session_state.get('user') or {},
                question_types=question_types,
                difficulty=difficulty,
                num_questions=num_questions,
                resume_id=resume_id,
            )
            return questions
    except Exception as e:
        st.error(f"Error Generating questions:{e}")
        return []


def render(client: BackendClient):
    if st.session_state.resume_analyzed and client:
        ui.interview_questions_section(
            has_resume=True,
            generate_questions_func=lambda types, diff, num: generate_interview_questions(client, types, diff, num),
        )
    else:
        st.warning("please upload and analyze a resume first in the 'Resume Analysis' tab.")
