import streamlit as st
import ui_restored_tmp as ui


def generate_interview_questions(agent, question_types, difficulty, num_questions):
    try:
        with st.spinner("Generating pesonalized interview questions..."):
            questions = agent.generate_interview_questions(question_types, difficulty, num_questions)
            return questions
    except Exception as e:
        st.error(f"Error Generating questions:{e}")
        return []


def render(agent):
    if st.session_state.resume_analyzed and agent:
        ui.interview_questions_section(
            has_resume=True,
            generate_questions_func=lambda types, diff, num: generate_interview_questions(agent, types, diff, num),
        )
    else:
        st.warning("please upload and analyze a resume first in the 'Resume Analysis' tab.")
