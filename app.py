import streamlit as st
from frontend.provider import setup_agent 
from dotenv import load_dotenv
load_dotenv()
from frontend import ui
from database import (
    save_user_settings,
)
from frontend.auth_ui import ensure_logged_in
from frontend.provider import setup_agent
from frontend.tabs import (
    resume_analysis,
    resume_qa,
    interview_questions,
    resume_improvement,
    cover_letter,
    job_search,
    mock_interview,
    latex_resume_update,
)
import atexit
import os
import requests
from frontend.backend_client import BackendClient

st.set_page_config(
    page_title = "ResuMate - Your AI Career Companion",
    page_icon = "🤖",
    layout  = "wide"
)

# Session state defaults to avoid missing attributes
if 'resume_agent' not in st.session_state:
    st.session_state.resume_agent = None
if 'resume_analyzed' not in st.session_state:
    st.session_state.resume_analyzed = False
if 'analysis_result' not in st.session_state:
    st.session_state.analysis_result = None
if 'api_key' not in st.session_state:
    st.session_state.api_key = None
if 'interview' not in st.session_state:
    st.session_state.interview = {
        'started': False,
        'completed': False,
        'current': 0,
        'questions': [],
        'answers': [],
        'transcripts': [],
        'per_q_scores': [],
        'summary': None,
        'start_time': None,
        'max_duration_sec': 15 * 60,
        'decision': None,
    }
if 'user' not in st.session_state:
    st.session_state.user = None
if 'user_settings' not in st.session_state:
    st.session_state.user_settings = {}

def cleanup():
    """clean up resources when the app exits"""
    if st.session_state.resume_agent:
        st.session_state.resume_agent.cleanup()
atexit.register(cleanup)        

def main():
    ui.setup_page()
    ui.display_header()
    # Backend health (optional): show FastAPI backend connectivity
    backend_url = os.getenv("BACKEND_URL", "http://localhost:8000")
    backend_status = "unknown"
    try:
        r = requests.get(f"{backend_url}/health", timeout=2)
        if r.ok and (r.json() or {}).get("status") == "ok":
            backend_status = "connected"
        else:
            backend_status = "unavailable"
    except Exception:
        backend_status = "unavailable"
    # Login gate
    if not ensure_logged_in():
        return
    
    config = ui.setup_sidebar() 
    us = st.session_state.get('user_settings') or {}
    if us:
        # Only set defaults if not provided in the current sidebar selection
        config.setdefault('provider', us.get('provider'))
        config.setdefault('model', us.get('model'))
    # Initialize backend client and (optionally) local agent
    client = BackendClient(base_url=backend_url)
    agent  = setup_agent(config)
    # Save the settings for this user
    try:
        if st.session_state.user:
            to_save = {
                'provider': st.session_state.get('provider'),
                'model': (st.session_state.get('groq_model') if st.session_state.get('provider')=='groq' else st.session_state.get('ollama_model')),
                'jooble_api_key': config.get('jooble_api_key') or (st.session_state.get('user_settings') or {}).get('jooble_api_key'),
                'api_key': config.get('api_key') or os.getenv('GROQ_API_KEY') or os.getenv('OPENAI_API_KEY'),
            }
            save_user_settings(st.session_state.user['id'], to_save)
            st.session_state.user_settings = to_save
    except Exception as e:
        st.info(f"Could not save settings: {e}")
    
    st.caption(f"Provider: {st.session_state.get('provider')} | Model: {st.session_state.get('groq_model') if st.session_state.get('provider')=='groq' else st.session_state.get('ollama_model')} | Analyzed: {st.session_state.get('resume_analyzed')} | Backend: {backend_status}")
    
    tabs  = ui.create_tabs()
    
    with tabs[0]:
        # Use backend for analysis
        resume_analysis.render(client)
            
    with tabs[1]:
        # Use backend for Q&A
        resume_qa.render(client)
    
    
    with tabs[2]:
        interview_questions.render(client)
            
    
    with tabs[3]:   # Resume Improvement tab
        resume_improvement.render(client)

    with tabs[4]:   # Cover Letter tab
        cover_letter.render(st.session_state.resume_agent)

    with tabs[5]:   # Job Search tab
        job_search.render(client)

    with tabs[6]:   # Mock Interview - Coming Soon
        mock_interview.render()

    with tabs[7]:   # LaTeX Resume Update - Coming Soon
        latex_resume_update.render()

  

if __name__ == "__main__" :
    main()
    