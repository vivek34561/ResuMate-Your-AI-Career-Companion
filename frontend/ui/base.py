import os
from typing import List, Tuple, Dict, Optional
import streamlit as st
from database import get_user_resumes


def setup_page():
    st.markdown(
        """
        <style>
            .main { padding: 2rem; }
            .stButton>button { width: 100%; }
            .stTextArea textarea { min-height: 150px; }
            .section { margin-bottom: 2rem; }
            .skill-score { padding: 0.5rem; border-radius: 0.5rem; margin-bottom: 0.5rem; }
            .good-score { background-color: #e6f7e6; }
            .medium-score { background-color: #fff8e6; }
            .low-score { background-color: #ffebeb; }
        </style>
        """,
        unsafe_allow_html=True,
    )


def display_header():
    st.title("🤖 ResuMate - Your AI Career Companion")
    st.markdown(
        """
        Upload a resume, select a target role or paste job description, and get personalized feedback to improve your job application.
        """
    )
    # st.divider()


def setup_sidebar() -> Dict:
    with st.sidebar:
        st.header("Configuration")
        _user = st.session_state.get("user")
        if _user:
            if _user.get("picture"):
                col_img, col_txt = st.columns([1, 3])
                with col_img:
                    st.image(_user["picture"], width=50)
                with col_txt:
                    st.markdown(f"**{_user.get('name') or _user.get('username','')}**")
                    if _user.get("email"):
                        st.caption(_user["email"])
            else:
                st.markdown(f"👤 **{_user.get('name') or _user.get('username','')}**")
                if _user.get("email"):
                    st.caption(_user["email"])

            if st.button("🚪 Logout", use_container_width=True):
                st.session_state.user = None
                st.session_state.user_settings = {}
                st.rerun()

        _user_settings = st.session_state.get("user_settings") or {}
        saved_resume_id = None
        saved_resumes = []
        if _user:
            try:
                saved_resumes = get_user_resumes(_user["id"]) or []
                if saved_resumes:
                    st.subheader("Saved Resumes")
                    labels = [
                        f"{r.get('filename') or 'resume'} · {str(r.get('created_at'))[:19]}" for r in saved_resumes
                    ]
                    ids = [r["id"] for r in saved_resumes]
                    default_idx = 0
                    if "selected_resume_id" in st.session_state:
                        try:
                            default_idx = ids.index(st.session_state["selected_resume_id"])
                        except ValueError:
                            default_idx = 0
                    sel = st.selectbox(
                        "Use a previously uploaded resume",
                        options=list(range(len(ids))),
                        format_func=lambda i: labels[i],
                        index=default_idx,
                    )
                    saved_resume_id = ids[sel]
                    st.session_state["selected_resume_id"] = saved_resume_id
                    
            except Exception as e:
                st.info(f"Could not load saved resumes: {e}")

        st.subheader("AI Provider")
        provider = "groq"
        api_key = st.text_input(
            "Enter Your Groq API Key (optional if set in .env)",
            value="",
            type="password",
            help="Leave empty to use GROQ_API_KEY from .env file, or enter your own key here",
            placeholder="gsk_...",
        )
        st.caption(
            "🎥 [**Watch: How to Get Groq API Key**](https://www.youtube.com/watch?v=nt1PJu47nTk) | [Get Free API Key](https://console.groq.com/keys)"
        )
        if not api_key or api_key.strip() == "":
            api_key = os.getenv("GROQ_API_KEY", "")
        else:
            st.caption("✅ Using your provided API key")

        groq_models = [
            "openai/gpt-oss-20b",
            "openai/gpt-oss-120b",
            "llama-3.3-70b-versatile",
            "Custom...",
        ]
        env_model = _user_settings.get("model") or os.getenv("GROQ_MODEL") or "openai/gpt-oss-20b"
        default_model_index = (
            groq_models.index(env_model) if env_model in groq_models else groq_models.index("Custom...")
        )
        preset = st.selectbox(
            "Groq preset model",
            options=groq_models,
            index=default_model_index,
            help="Choose a known model or select Custom to provide a model id",
        )
        if preset == "Custom...":
            model = st.text_input(
                "Custom Groq model id",
                value=env_model if env_model not in groq_models else "",
                help="Enter an exact model id available to your Groq account",
            )
        else:
            model = preset

        jooble_api_key = os.getenv("JOOBLE_API_KEY", "")

        st.markdown("---")
        st.markdown(
            """
            **How to use:**
            1. Enter your API key (auto-filled from .env if present)
            2. Upload your resume
            3. Select target role or paste job description
            4. Click 'Analyze Resume'
            5. Explore the different tabs for insights
            """
        )
        st.markdown("---")
        st.markdown(
            """
            **Note:** This tool uses AI to analyze resumes and generate suggestions. 
            Always review the outputs carefully before using them.
            """
        )

    config = {
        "provider": provider,
        "api_key": api_key,
        "model": model,
        "jooble_api_key": jooble_api_key,
    }
    if saved_resume_id:
        config["selected_resume_id"] = saved_resume_id
    return config


def create_tabs() -> List:
    return st.tabs(
        [
            "📝 Resume Analysis",
            "💬 Ask anything about your resume",
            "💡 Generate Interview Questions",
            "✨ Resume Improvement",
            "✉️ Generate Cover Letter",
            "🔍 Job Search",
            "🧩 LaTeX Resume Update",
        ]
    )


def role_selection_section(role_requirements: Dict) -> Tuple[str, Optional[str]]:
    st.subheader("Target Role Selection")
    col1, col2 = st.columns([1, 2])
    with col1:
        role = st.selectbox(
            "Select Target Role",
            options=list(role_requirements.keys()),
            index=0,
        )
    with col2:
        st.markdown("**OR**")
        custom_jd = st.text_area(
            "Paste Job Description (overrides role selection)",
            height=200,
            placeholder="Paste the full job description here if you want analysis against a specific job...",
        )
    return role, custom_jd if custom_jd else None


def resume_upload_section():
    st.header("📄 Resume Selection")
    _user = st.session_state.get("user")
    has_saved_resumes = False
    saved_resumes = []
    if _user:
        try:
            saved_resumes = get_user_resumes(_user["id"]) or []
            has_saved_resumes = len(saved_resumes) > 0
        except Exception:
            pass
    if has_saved_resumes:
        resume_source = st.radio(
            "Choose resume source:",
            ["📤 Upload New Resume", "💾 Use Saved Resume"],
            horizontal=True,
            help="Select whether to upload a new resume or use a previously saved one",
        )
    else:
        resume_source = "📤 Upload New Resume"
        if _user:
            st.info("💡 Tip: After analyzing a resume, it will be saved for quick reuse!")

    uploaded_file = None
    if resume_source == "📤 Upload New Resume":
        uploaded_file = st.file_uploader(
            label="Upload your resume (PDF or TXT)",
            type=["pdf", "txt"],
            key="new_resume_upload",
        )
        if uploaded_file is not None:
            file_details = {
                "filename": uploaded_file.name,
                "filetype": uploaded_file.type,
                "filesize": uploaded_file.size,
            }
            st.write(file_details)
            if "use_saved_resume_id" in st.session_state:
                del st.session_state["use_saved_resume_id"]
            return uploaded_file
    else:
        st.markdown("**Select a saved resume:**")
        resume_options = []
        resume_ids = []
        for r in saved_resumes:
            filename = r.get("filename") or "Resume"
            created = str(r.get("created_at", ""))[:19]
            resume_options.append(f"{filename} (saved on {created})")
            resume_ids.append(r["id"])
        selected_idx = st.selectbox(
            "Saved Resumes",
            options=range(len(resume_options)),
            format_func=lambda i: resume_options[i],
            key="saved_resume_selector",
        )
        if selected_idx is not None and selected_idx < len(resume_ids):
            selected_resume_id = resume_ids[selected_idx]
            st.session_state["use_saved_resume_id"] = selected_resume_id
            selected_resume = saved_resumes[selected_idx]
            st.success(f"✅ Using saved resume: **{selected_resume.get('filename', 'Resume')}**")
            resume_text = selected_resume.get("resume_text", "")
            if resume_text:
                with st.expander("📄 Preview Resume Content"):
                    st.text_area(
                        "Resume Preview",
                        resume_text[:500] + "..." if len(resume_text) > 500 else resume_text,
                        height=150,
                        disabled=True,
                    )
            return "USE_SAVED_RESUME"
    return None
