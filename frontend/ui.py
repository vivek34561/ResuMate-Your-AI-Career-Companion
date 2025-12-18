import streamlit as st
import os
from typing import List, Tuple, Dict, Callable, Optional
from database import get_user_resumes

# Re-exported helpers used by app.py and tab modules

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
        *Get resume-ready, interview-ready, and hire-ready with AI-powered insights*
        
        Upload a resume, select a target role or paste job description, and get personalized feedback to improve your job application.
        """
    )
    st.divider()


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
                    st.markdown("---")
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
                    st.caption(
                        "Tip: Click Analyze in the main page to analyze this saved resume without re-embedding."
                    )
            except Exception as e:
                st.info(f"Could not load saved resumes: {e}")

        st.subheader("AI Provider")
        st.caption("Using Groq for all AI features")
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
            if api_key:
                st.caption("✅ Using API key from .env file")
            else:
                st.warning(
                    "⚠️ No API key provided. Please enter your Groq API key or set GROQ_API_KEY in .env file"
                )
        else:
            st.caption("✅ Using your provided API key")

        groq_models = [
            "llama-3.3-70b-versatile",
            "mixtral-8x7b-32768",
            "llama-3.1-8b-instant",
            "Custom...",
        ]
        env_model = _user_settings.get("model") or os.getenv("GROQ_MODEL") or "llama-3.1-8b-instant"
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

        st.markdown("---")
        st.subheader("Job APIs")
        existing_jooble = (_user_settings.get("jooble_api_key") if _user_settings else None) or os.getenv(
            "JOOBLE_API_KEY", ""
        )
        jooble_api_key = st.text_input(
            "Jooble API Key (per user)",
            value=existing_jooble,
            type="password",
            help="Used for Jooble job search. Stored in your user settings.",
        )

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
            "💬 Resume Chatbot",
            "💡 Interview Questions",
            "✨ Resume Improvement",
            "✉️ Cover Letter",
            "🔍 Job Search",
            "🎤 Mock Interview",
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

def get_score_description(score: int) -> str:
    if score >= 9:
        return "Excellent demonstration of this skill"
    elif score >= 7:
        return "Good demonstration of this skill"
    elif score >= 5:
        return "Moderate demonstration - could be improved"
    elif score >= 3:
        return "Weak demonstration - needs improvement"
    else:
        return "Very weak or missing - significant improvement needed"

def display_analysis_results(analysis_result: Dict):
    st.markdown(
        """
        <div style='text-align: center; padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 10px; margin-bottom: 30px;'>
            <h1 style='color: white; margin: 0;'>📊 Resume Analysis Report</h1>
            <p style='color: white; margin: 10px 0 0 0; opacity: 0.9;'>Comprehensive AI-powered evaluation of your resume</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("## 📈 Key Performance Indicators")
    score = analysis_result.get("overall_score", 0)
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(
            label="🎯 Overall Score",
            value=f"{score}%",
            delta=f"{score - 70}% from avg" if score >= 70 else f"{score - 70}% below avg",
            help="Your overall match score compared to job requirements",
        )
    with col2:
        matching_skills = len(analysis_result.get("strengths", []))
        st.metric(label="✅ Matching Skills", value=matching_skills)
    with col3:
        missing_skills = len(analysis_result.get("missing_skills", []))
        st.metric(label="⚠️ Missing Skills", value=missing_skills, delta=f"-{missing_skills}" if missing_skills > 0 else "Perfect!", delta_color="inverse")
    with col4:
        avg_skill_score = sum(analysis_result.get("skill_scores", {}).values()) / max(len(analysis_result.get("skill_scores", {})), 1)
        st.metric(label="📊 Avg Skill Level", value=f"{avg_skill_score:.1f}/10")
    st.markdown("---")
    st.markdown("## 📊 Visual Analytics")
    tab1, tab2, tab3 = st.tabs(["📈 Score Overview", "🎯 Skill Analysis", "📉 Gap Analysis"])
    with tab1:
        st.markdown("### Overall Performance Gauge")
        try:
            import plotly.graph_objects as go
            fig = go.Figure(
                go.Indicator(
                    mode="gauge+number+delta",
                    value=score,
                    domain={'x': [0, 1], 'y': [0, 1]},
                    title={'text': "Resume Match Score", 'font': {'size': 24}},
                    delta={'reference': 70, 'increasing': {'color': "green"}},
                    gauge={
                        'axis': {'range': [None, 100], 'tickwidth': 1, 'tickcolor': "darkblue"},
                        'bar': {'color': "darkblue"},
                        'bgcolor': "white",
                        'borderwidth': 2,
                        'bordercolor': "gray",
                        'steps': [
                            {'range': [0, 50], 'color': '#ffcdd2'},
                            {'range': [50, 70], 'color': '#fff9c4'},
                            {'range': [70, 85], 'color': '#c8e6c9'},
                            {'range': [85, 100], 'color': '#81c784'},
                        ],
                        'threshold': {'line': {'color': "red", 'width': 4}, 'thickness': 0.75, 'value': 70},
                    },
                )
            )
            fig.update_layout(height=300, margin=dict(l=20, r=20, t=50, b=20), paper_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig, use_container_width=True)
        except Exception:
            st.info("Install plotly for rich visuals: pip install plotly")
    with tab2:
        st.markdown("### Skill Proficiency Analysis")
        skill_scores = analysis_result.get("skill_scores", {})
        if skill_scores:
            try:
                import plotly.express as px
                import pandas as pd
                skills_df = pd.DataFrame([
                    {"Skill": skill, "Score": s, "Category": "Strong" if s >= 7 else "Moderate" if s >= 4 else "Weak"}
                    for skill, s in sorted(skill_scores.items(), key=lambda x: x[1], reverse=True)
                ])
                fig = px.bar(
                    skills_df,
                    y="Skill",
                    x="Score",
                    color="Category",
                    orientation='h',
                    title="Skill Proficiency Levels",
                    labels={"Score": "Proficiency Score (0-10)"},
                    color_discrete_map={"Strong": "#4CAF50", "Moderate": "#FF9800", "Weak": "#F44336"},
                    height=max(400, len(skills_df) * 30),
                )
                fig.update_layout(xaxis=dict(range=[0, 10]), yaxis={'categoryorder': 'total ascending'})
                st.plotly_chart(fig, use_container_width=True)
            except Exception:
                st.info("Install plotly and pandas for skill charts: pip install plotly pandas")
        else:
            st.info("No detailed skill scores available")
    with tab3:
        st.markdown("### Skills Gap Analysis")
        col_gap1, col_gap2 = st.columns(2)
        with col_gap1:
            st.markdown("#### ✅ **Your Strengths**")
            strengths = analysis_result.get("strengths", [])
            if strengths:
                for i, strength in enumerate(strengths, 1):
                    st.markdown(f"<div style='padding: 10px; margin: 5px 0; background-color: #e8f5e9; border-left: 4px solid #4CAF50; border-radius: 5px;'><b>{i}.</b> {strength}</div>", unsafe_allow_html=True)
            else:
                st.info("No specific strengths identified")
        with col_gap2:
            st.markdown("#### ⚠️ **Areas for Improvement**")
            missing_skills = analysis_result.get("missing_skills", [])
            if missing_skills:
                for i, skill in enumerate(missing_skills, 1):
                    st.markdown(f"<div style='padding: 10px; margin: 5px 0; background-color: #fff3e0; border-left: 4px solid #FF9800; border-radius: 5px;'><b>{i}.</b> {skill}</div>", unsafe_allow_html=True)
            else:
                st.success("✅ No major skill gaps identified!")
    st.markdown("---")

def resume_qa_section(has_resume: bool, ask_question_func: Callable):
    st.subheader("💬 Resume AI Chatbot")
    st.markdown("Ask me anything about the resume!")
    if has_resume:
        if 'chat_history' not in st.session_state:
            st.session_state.chat_history = []
        chat_container = st.container(height=500)
        with chat_container:
            for i, message in enumerate(st.session_state.chat_history):
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

def cover_letter_section(has_resume: bool, generate_cover_letter_func: Callable):
    st.subheader("Generate a Tailored Cover Letter")
    if has_resume:
        col1, col2 = st.columns(2)
        with col1:
            company = st.text_input("Company Name", placeholder="e.g. Acme Corp")
            role = st.text_input("Role / Position", placeholder="e.g. Machine Learning Engineer")
            tone = st.selectbox("Tone", ["professional", "enthusiastic", "confident", "concise"], index=0)
        with col2:
            length = st.selectbox("Length", ["short (~250-300 words)", "one-page (~400-500 words)"], index=0)
        jd = st.text_area("Paste Job Description (optional)", height=200, placeholder="Paste the full JD to tailor the letter more precisely")
        if st.button("Generate Cover Letter", type="primary"):
            if not company or not role:
                st.warning("Please provide both company and role.")
            else:
                with st.spinner("Writing your letter..."):
                    letter = generate_cover_letter_func(company, role, jd, tone, "one-page" if length.startswith("one-page") else "short")
                if letter and not letter.startswith("Error"):
                    st.markdown("### Cover Letter")
                    st.text_area("Letter", letter, height=500, key="cover_letter_output")
                    st.download_button(label="Download Cover Letter", data=letter, file_name="cover_letter.txt", mime="text/plain")
                else:
                    st.error(letter or "No letter generated.")
    else:
        st.warning("Please upload and analyze a resume first")

def latex_resume_update_section(has_resume: bool, update_latex_func: Callable):
    st.subheader("Update Your LaTeX Resume for a Specific JD")
    st.caption("Paste your current LaTeX resume code and the target JD. We'll tailor the content while keeping your LaTeX format unchanged.")
    col1, col2 = st.columns(2)
    with col1:
        latex_src = st.text_area("Your LaTeX Resume Source", height=350, placeholder="\\documentclass{resume}\n% ... preamble ...\n\\begin{document}\n% ... your resume ...\n\\end{document}")
    with col2:
        jd = st.text_area("Job Description", height=350, placeholder="Paste the full job description here")
    if st.button("Update LaTeX Resume", type="primary"):
        if not latex_src or not latex_src.strip():
            st.warning("Please paste your LaTeX resume source.")
        elif not jd or not jd.strip():
            st.warning("Please paste the job description.")
        else:
            with st.spinner("Updating LaTeX resume..."):
                updated = update_latex_func(latex_src, jd)
            if updated and not updated.startswith("Error"):
                st.markdown("### Updated LaTeX Resume")
                st.text_area("LaTeX Output", updated, height=500, key="updated_latex_output")
                st.download_button(label="Download Updated LaTeX", data=updated, file_name="updated_resume.tex", mime="text/plain")
            else:
                st.error(updated or "No updated LaTeX generated.")

def resume_improvement_section(has_resume: bool, improve_resume_func: Callable, get_improved_resume_func: Callable):
    st.subheader("✨ Resume Improvement Suggestions")
    st.markdown("Get AI-powered suggestions to enhance your resume and make it stand out!")

    if has_resume:
        col1, col2 = st.columns([1, 1])

        with col1:
            st.markdown("#### 📋 Improvement Areas")
            improvement_areas = st.multiselect(
                "Select areas to improve",
                options=[
                    "Skills Highlighting",
                    "Work Experience",
                    "Achievements & Impact",
                    "Keywords & ATS Optimization",
                    "Professional Summary",
                    "Education & Certifications",
                    "Formatting & Structure",
                ],
                default=["Skills Highlighting", "Work Experience", "Achievements & Impact"],
                help="Choose specific areas where you want improvement suggestions",
            )

        with col2:
            st.markdown("#### 🎯 Target Role (Optional)")
            target_role = st.text_input(
                "Target Role",
                placeholder="e.g., Senior Software Engineer, Data Scientist",
                help="Specify a target role for more focused suggestions",
            )

        col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 1])
        with col_btn2:
            if st.button("🔍 Generate Improvement Suggestions", type="primary", use_container_width=True):
                if improvement_areas:
                    with st.spinner("Analyzing your resume and generating personalized suggestions..."):
                        improvements = improve_resume_func(improvement_areas, target_role or "")
                        st.session_state['improvement_suggestions'] = improvements
                        st.success("✅ Improvement suggestions generated!")
                        st.rerun()
                else:
                    st.warning("Please select at least one improvement area.")

        if 'improvement_suggestions' in st.session_state and st.session_state['improvement_suggestions']:
            st.markdown("---")
            st.markdown(
                """
                <div style='text-align: center; padding: 15px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 10px; margin-bottom: 20px;'>
                    <h2 style='color: white; margin: 0;'>💡 Your Personalized Improvement Suggestions</h2>
                </div>
                """,
                unsafe_allow_html=True,
            )

            improvements = st.session_state['improvement_suggestions']

            total_suggestions = sum(
                len(details.get('specific', [])) if isinstance(details, dict) else 1
                for details in improvements.values()
            )

            col_metric1, col_metric2, col_metric3 = st.columns(3)
            with col_metric1:
                st.metric("📋 Areas Analyzed", len(improvements))
            with col_metric2:
                st.metric("💡 Total Suggestions", total_suggestions)
            with col_metric3:
                st.metric("✅ Completion Status", "Ready to Apply")

            st.markdown("---")

            for idx, (area, details) in enumerate(improvements.items(), 1):
                if any(word in area.lower() for word in ['skill', 'experience', 'achievement']):
                    border_color = "#4CAF50"
                    bg_color = "#e8f5e9"
                    icon = "🎯"
                elif any(word in area.lower() for word in ['keyword', 'ats', 'optimization']):
                    border_color = "#FF9800"
                    bg_color = "#fff3e0"
                    icon = "📊"
                else:
                    border_color = "#2196F3"
                    bg_color = "#e3f2fd"
                    icon = "✨"

                with st.expander(f"{icon} **{idx}. {area}**", expanded=(idx <= 2)):
                    if isinstance(details, dict):
                        if 'description' in details and details['description']:
                            st.markdown(
                                f"""
                                <div style='background-color: {bg_color}; padding: 15px; border-left: 5px solid {border_color}; border-radius: 5px; margin-bottom: 15px;'>
                                    <h4 style='margin: 0; color: #333;'>📋 Overview</h4>
                                    <p style='margin: 10px 0 0 0; color: #555;'>{details['description']}</p>
                                </div>
                                """,
                                unsafe_allow_html=True,
                            )

                        if 'specific' in details and details['specific']:
                            st.markdown("#### 🔧 Actionable Improvements")
                            st.markdown("Follow these specific steps to enhance this area:")

                            for idx_sub, suggestion in enumerate(details['specific'], 1):
                                st.markdown(
                                    f"""
                                    <div style='background-color: white; padding: 12px; margin: 8px 0; border-left: 4px solid {border_color}; border-radius: 5px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);'>
                                        <b style='color: {border_color};'>Step {idx_sub}:</b> {suggestion}
                                    </div>
                                    """,
                                    unsafe_allow_html=True,
                                )

                        if 'before_after' in details and details['before_after']:
                            st.markdown("#### 📝 Example Transformation")
                            ba = details['before_after']

                            col_before, col_after = st.columns(2)
                            with col_before:
                                st.markdown("**❌ Before (Weak)**")
                                st.markdown(
                                    f"""
                                    <div style='background-color: #ffebee; padding: 15px; border-radius: 5px; border: 2px solid #ef5350;'>
                                        <p style='margin: 0; color: #c62828; font-style: italic;'>{ba.get('before', 'N/A')}</p>
                                    </div>
                                    """,
                                    unsafe_allow_html=True,
                                )

                            with col_after:
                                st.markdown("**✅ After (Strong)**")
                                st.markdown(
                                    f"""
                                    <div style='background-color: #e8f5e9; padding: 15px; border-radius: 5px; border: 2px solid #66bb6a;'>
                                        <p style='margin: 0; color: #2e7d32; font-weight: 500;'>{ba.get('after', 'N/A')}</p>
                                    </div>
                                    """,
                                    unsafe_allow_html=True,
                                )

                            st.success("💡 **Key Improvement:** The 'After' version is more specific, quantifiable, and impact-focused.")
                    else:
                        st.markdown(str(details))

            st.markdown("---")
            st.markdown("### 📄 Generate Improved Resume")
            st.markdown("Want an AI-rewritten version of your resume incorporating these suggestions?")

            col1, col2 = st.columns([2, 1])
            with col1:
                highlight_skills = st.text_area(
                    "Skills to highlight (comma-separated) or paste Job Description",
                    placeholder="Python, Machine Learning, AWS, Docker... OR paste full job description",
                    help="Enter specific skills to emphasize or paste a full job description for targeted optimization",
                )

            with col2:
                st.markdown("")
                st.markdown("")
                if st.button("✨ Generate Improved Resume", use_container_width=True):
                    with st.spinner("Generating your improved resume..."):
                        improved_resume = get_improved_resume_func(target_role or "", highlight_skills)
                        st.session_state['improved_resume_text'] = improved_resume
                        st.success("✅ Improved resume generated!")
                        st.rerun()

            if 'improved_resume_text' in st.session_state and st.session_state['improved_resume_text']:
                st.markdown("---")
                st.markdown(
                    """
                    <div style='text-align: center; padding: 15px; background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%); border-radius: 10px; margin-bottom: 20px;'>
                        <h2 style='color: white; margin: 0;'>📝 Your Improved Resume</h2>
                        <p style='color: white; margin: 5px 0 0 0; opacity: 0.9;'>Enhanced with AI recommendations</p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                st.markdown("### ✨ Key Improvements Applied")
                col_imp1, col_imp2, col_imp3, col_imp4 = st.columns(4)
                with col_imp1:
                    st.markdown(
                        """
                        <div style='background-color: #e8f5e9; padding: 15px; border-radius: 10px; text-align: center;'>
                            <h3 style='margin: 0; color: #4CAF50;'>✅</h3>
                            <p style='margin: 5px 0 0 0; color: #2e7d32; font-weight: bold;'>Keywords Optimized</p>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                with col_imp2:
                    st.markdown(
                        """
                        <div style='background-color: #e3f2fd; padding: 15px; border-radius: 10px; text-align: center;'>
                            <h3 style='margin: 0; color: #2196F3;'>📊</h3>
                            <p style='margin: 5px 0 0 0; color: #1565c0; font-weight: bold;'>Metrics Added</p>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                with col_imp3:
                    st.markdown(
                        """
                        <div style='background-color: #fff3e0; padding: 15px; border-radius: 10px; text-align: center;'>
                            <h3 style='margin: 0; color: #FF9800;'>💪</h3>
                            <p style='margin: 5px 0 0 0; color: #e65100; font-weight: bold;'>Impact Enhanced</p>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                with col_imp4:
                    st.markdown(
                        """
                        <div style='background-color: #f3e5f5; padding: 15px; border-radius: 10px; text-align: center;'>
                            <h3 style='margin: 0; color: #9C27B0;'>🎯</h3>
                            <p style='margin: 5px 0 0 0; color: #6a1b9a; font-weight: bold;'>ATS Friendly</p>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                st.markdown("---")

                with st.expander("📋 See Detailed Changes Applied", expanded=False):
                    st.markdown(
                        """
                        **What we improved in your resume:**

                        ✅ **Keywords & ATS Optimization**
                        - Added industry-specific keywords
                        - Optimized for Applicant Tracking Systems
                        - Improved searchability for recruiters

                        📊 **Quantifiable Achievements**
                        - Added metrics and numbers where possible
                        - Highlighted measurable impact

                        💪 **Action Verbs & Impact**
                        - Replaced weak verbs with strong action words
                        - Emphasized results and outcomes

                        🎯 **Structure & Formatting**
                        - Improved readability and flow
                        - Enhanced section organization
                        - Made key points stand out

                        🔍 **Role Alignment**
                        - Tailored content to target role
                        - Highlighted relevant experience
                        - Emphasized matching skills
                        """
                    )

                st.markdown("### 📄 Improved Resume Content")
                tab1, tab2 = st.tabs(["📝 Full Resume", "🔍 Comparison View"])
                with tab1:
                    st.markdown("**Your enhanced resume is ready! Copy the text below or download it.**")
                    st.text_area(
                        "Enhanced Resume",
                        value=st.session_state['improved_resume_text'],
                        height=500,
                        help="Copy this improved version or download it below",
                        key="improved_resume_display",
                    )
                    col_dl1, col_dl2, col_dl3 = st.columns(3)
                    with col_dl1:
                        st.download_button(
                            label="📥 Download as TXT",
                            data=st.session_state['improved_resume_text'],
                            file_name="improved_resume.txt",
                            mime="text/plain",
                            use_container_width=True,
                        )
                    with col_dl2:
                        markdown_content = f"# Improved Resume\n\n{st.session_state['improved_resume_text']}"
                        st.download_button(
                            label="📥 Download as MD",
                            data=markdown_content,
                            file_name="improved_resume.md",
                            mime="text/markdown",
                            use_container_width=True,
                        )
                    with col_dl3:
                        if st.button("📋 Copy to Clipboard", use_container_width=True):
                            st.info("💡 Select the text above and use Ctrl+C (Windows) or Cmd+C (Mac) to copy!")
                with tab2:
                    st.markdown("### 🔄 Before vs After Comparison")
                    st.info("💡 Compare your original resume with the improved version side-by-side")
                    col_orig, col_new = st.columns(2)
                    with col_orig:
                        st.markdown("#### 📄 Original Resume")
                        original_text = getattr(st.session_state.get('resume_agent'), 'resume_text', 'Original resume not available')
                        st.text_area(
                            "Original",
                            value=original_text[:2000] if len(original_text) > 2000 else original_text,
                            height=400,
                            disabled=True,
                            key="original_resume_view",
                        )
                        if len(original_text) > 2000:
                            st.caption("📝 Showing first 2000 characters")
                    with col_new:
                        st.markdown("#### ✨ Improved Resume")
                        st.text_area(
                            "Improved",
                            value=st.session_state['improved_resume_text'][:2000] if len(st.session_state['improved_resume_text']) > 2000 else st.session_state['improved_resume_text'],
                            height=400,
                            disabled=True,
                            key="improved_resume_compare_view",
                        )
                        if len(st.session_state['improved_resume_text']) > 2000:
                            st.caption("📝 Showing first 2000 characters")
                    st.success("✅ Notice the improvements: stronger action verbs, quantified achievements, better keywords, and ATS optimization!")
    else:
        st.warning("Please upload and analyze a resume first in the 'Resume Analysis' tab.")
