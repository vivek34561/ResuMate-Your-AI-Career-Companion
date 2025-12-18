from typing import Callable
import streamlit as st


def interview_questions_section(has_resume: bool, generate_questions_func: Callable):
    st.subheader("Generate Personalized Interview Questions")
    if has_resume:
        col1, col2, col3 = st.columns(3)
        with col1:
            question_types = st.multiselect(
                "Question Types",
                options=["Technical", "Projects", "Behavioral", "Situational", "System Design", "Problem Solving"],
                default=["Technical", "Behavioral"],
            )
        with col2:
            difficulty = st.selectbox("Difficulty Level", options=["Easy", "Medium", "Hard", "Mixed"], index=1)
        with col3:
            num_questions = st.slider("Number of Questions", min_value=5, max_value=20, value=10, step=1)
        if st.button("Generate Questions", type="primary"):
            questions = generate_questions_func(question_types, difficulty, num_questions)
            if questions:
                st.markdown("### Generated Questions")
                for i, q in enumerate(questions, 1):
                    question = q.get("question", "N/A")
                    solution = q.get("solution") or ""
                    with st.expander(f"{i}. {question}"):
                        if solution:
                            st.markdown("**Solution:**")
                            st.write(solution)
                        else:
                            st.info("No solution generated for this question.")
            else:
                st.warning("No questions were generated. Please try again with different parameters.")
    else:
        st.warning("Please upload and analyze a resume first")
