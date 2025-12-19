import streamlit as st
from frontend import ui
from frontend.backend_client import BackendClient


def ask_question(client: BackendClient, question, chat_history=None):
    try:
        with st.spinner("Generating response via backend..."):
            resume_id = st.session_state.get("active_resume_id") or st.session_state.get("use_saved_resume_id") or st.session_state.get("selected_resume_id")
            resp = client.ask_question(st.session_state.get('user') or {}, question, chat_history, resume_id=resume_id)
            return resp.get("answer")
    except Exception as e:
        return f"Error:{e}"


def render(client: BackendClient):
    if st.session_state.resume_analyzed and client:
        ui.resume_qa_section(
            has_resume=True,
            ask_question_func=lambda q, h=None: ask_question(client, q, h),
        )
    else:
        st.warning("Please upload and analyze a resume first in the 'Resume Analysis' tab.")
