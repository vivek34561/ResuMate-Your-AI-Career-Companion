import os
import io
import wave
import streamlit as st
from agents import ResumeAnalysisAgent

# OpenAI client (optional)
try:
    from openai import OpenAI
except Exception:
    OpenAI = None


def _get_client(api_key: str):
    if st.session_state.get('provider', 'openai') != 'openai':
        raise RuntimeError("OpenAI client requested but provider is not set to OpenAI.")
    if OpenAI is None:
        raise RuntimeError("openai package not found. Install with: pip install openai>=1.0.0")
    return OpenAI(api_key=api_key)


def setup_agent(config):
    provider = config.get("provider", "groq")
    if provider == 'groq':
        api_key = config.get("api_key") or os.getenv("GROQ_API_KEY")
        selected_model = config.get("model") or os.getenv("GROQ_MODEL") or "llama-3.1-8b-instant"
        if not api_key:
            st.error("Please provide your GROQ_API_KEY (or set it in .env).")
            st.stop()
    else:  # openai
        api_key = config.get("api_key") or os.getenv("OPENAI_API_KEY")
        selected_model = None
        if not api_key:
            st.error("Please provide your OPENAI_API_KEY (or set it in .env).")
            st.stop()

    st.session_state.provider = provider
    st.session_state.api_key = api_key
    if provider == 'groq':
        st.session_state.groq_model = selected_model

    if st.session_state.resume_agent is None:
        st.session_state.resume_agent = ResumeAnalysisAgent(
            api_key=api_key,
            model=st.session_state.get('groq_model'),
            provider=provider,
            user_id=(st.session_state.user['id'] if st.session_state.user else None),
            vector_cache_dir=os.getenv('VECTOR_CACHE_DIR') or '.cache/faiss'
        )
    else:
        st.session_state.resume_agent.api_key = api_key
        st.session_state.resume_agent.provider = provider
        st.session_state.resume_agent.model = st.session_state.get('groq_model')
        try:
            st.session_state.resume_agent.user_id = (st.session_state.user['id'] if st.session_state.user else None)
        except Exception:
            pass
    return st.session_state.resume_agent
