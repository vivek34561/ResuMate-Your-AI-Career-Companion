import streamlit as st
from frontend.provider import setup_agent 
from dotenv import load_dotenv
load_dotenv()
from frontend import ui
from frontend.provider import setup_agent
from frontend.tabs import (
    resume_analysis,
    resume_qa,
    interview_questions,
    resume_improvement,
    cover_letter,
    job_search,
    latex_resume_update,
)
import atexit
import os

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
    
    config = ui.setup_sidebar() 
    us = st.session_state.get('user_settings') or {}
    if us:
        # Only set defaults if not provided in the current sidebar selection
        config.setdefault('provider', us.get('provider'))
        config.setdefault('model', us.get('model'))
    # Initialize local agent for features that still use it (e.g., cover letter)
    agent  = setup_agent(config)
    # Persist settings locally in session (no login/DB)
    try:
        to_save = {
            'provider': st.session_state.get('provider'),
            'model': st.session_state.get('groq_model'),
            'jooble_api_key': config.get('jooble_api_key') or (st.session_state.get('user_settings') or {}).get('jooble_api_key'),
            'api_key': config.get('api_key') or os.getenv('GROQ_API_KEY') or os.getenv('OPENAI_API_KEY'),
        }
        st.session_state.user_settings = to_save
    except Exception as e:
        st.info(f"Could not save settings locally: {e}")
    
    st.caption(f"Provider: {st.session_state.get('provider')} | Model: {st.session_state.get('groq_model')} | Analyzed: {st.session_state.get('resume_analyzed')}")
    
    tabs  = ui.create_tabs()
    
    with tabs[0]:
        # Local analysis (no backend)
        resume_analysis.render()
            
    with tabs[1]:
        # Local Q&A (no backend)
        resume_qa.render()
    
    
    with tabs[2]:
        interview_questions.render()
            
    
    with tabs[3]:   # Resume Improvement tab (local agent)
        resume_improvement.render()

    with tabs[4]:   # Cover Letter tab
        cover_letter.render(st.session_state.resume_agent)

    with tabs[5]:   # Job Search tab (local agent)
        job_search.render()

    with tabs[6]:   # LaTeX Resume Update - Coming Soon
        latex_resume_update.render()

  

if __name__ == "__main__" :
    main()
    