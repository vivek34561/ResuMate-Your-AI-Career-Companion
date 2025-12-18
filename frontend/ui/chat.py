from typing import Callable
import streamlit as st


def resume_qa_section(has_resume: bool, ask_question_func: Callable):
    st.subheader("💬 Resume AI Chatbot")
    st.markdown("Ask me anything about the resume!")
    if has_resume:
        if 'chat_history' not in st.session_state:
            st.session_state.chat_history = []
        chat_container = st.container(height=500)
        with chat_container:
            for message in st.session_state.chat_history:
                if message['role'] == 'user':
                    with st.chat_message("user", avatar="👤"):
                        st.markdown(message['content'])
                else:
                    with st.chat_message("assistant", avatar="🤖"):
                        st.markdown(message['content'])
        user_question = st.chat_input("Ask a question about the resume...")
        if user_question:
            st.session_state.chat_history.append({'role': 'user', 'content': user_question})
            with st.spinner("🤔 Thinking..."):
                response = ask_question_func(user_question, st.session_state.chat_history[:-1])
            st.session_state.chat_history.append({'role': 'assistant', 'content': response})
            st.rerun()
        if st.session_state.chat_history:
            col1, col2, col3 = st.columns([1, 1, 1])
            with col2:
                if st.button("🗑️ Clear Chat History", use_container_width=True):
                    st.session_state.chat_history = []
                    st.rerun()
    else:
        st.warning("Please upload and analyze a resume first")
