import streamlit as st
import ui_restored_tmp as ui


def ask_question(agent, question, chat_history=None):
    try:
        with st.spinner("Generating response..."):
            response = agent.ask_question(question, chat_history)
            return response
    except Exception as e:
        return f"Error:{e}"


def render(agent):
    if st.session_state.resume_analyzed and agent:
        ui.resume_qa_section(
            has_resume=True,
            ask_question_func=lambda q, h=None: ask_question(agent, q, h),
        )
    else:
        st.warning("Please upload and analyze a resume first in the 'Resume Analysis' tab.")
