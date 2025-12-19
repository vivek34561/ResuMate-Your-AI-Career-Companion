import os
import json
import streamlit as st
from frontend import ui
from agents import ResumeAnalysisAgent
from database import save_user_resume, get_user_resume_by_id

ROLE_REQUIREMENTS = {
    "AI/ML Engineer": [
        "Python", "TensorFlow", "Machine Learning", "Deep Learning", "LangChain",
        "MLOps", "Scikit-learn", "Natural Language Processing (NLP)", "Hugging Face",
        "SQL", "Git", "Experiment Tracking (MLflow, DVC)"
    ],
    "Frontend Engineer": [
        "React", "Vue", "Angular", "HTML5", "CSS3", "JavaScript", "TypeScript",
        "Next.js", "Svelte", "Bootstrap", "Tailwind CSS", "GraphQL", "Redux",
        "WebAssembly", "Three.js", "Performance Optimization", "REST APIs",
        "Webpack", "Vite", "Responsive Design", "UI/UX Principles", "Testing (Jest, Cypress)"
    ],
    "Backend Engineer": [
        "Python", "Java", "Node.js", "Go", "REST APIs", "GraphQL", "gRPC",
        "Spring Boot", "Flask", "FastAPI", "Express.js", "Django",
        "SQL Databases", "NoSQL Databases", "PostgreSQL", "MySQL", "MongoDB",
        "Redis", "RabbitMQ", "Kafka", "Microservices", "Docker", "Kubernetes",
        "Cloud Services (AWS, GCP, Azure)", "CI/CD", "API Security", "Scalability & Performance Optimization"
    ],
    "Full Stack Developer": [
        "HTML5", "CSS3", "JavaScript", "TypeScript", "React", "Vue", "Angular",
        "Next.js", "Node.js", "Express.js", "Python", "Java", "Flask", "FastAPI",
        "Spring Boot", "SQL Databases", "NoSQL Databases", "PostgreSQL", "MySQL", "MongoDB",
        "REST APIs", "GraphQL", "Docker", "Kubernetes", "Microservices",
        "Cloud Services (AWS, GCP, Azure)", "Git", "CI/CD",
        "Responsive Design", "UI/UX Principles", "Testing (Jest, Cypress, PyTest)",
        "Performance Optimization", "API Security", "Version Control"
    ],
    "Data Scientist": [
        "Python", "SQL", "Machine Learning", "Deep Learning", "Scikit-learn",
        "TensorFlow/PyTorch", "Natural Language Processing (NLP)/Computer Vision",
        "Data Visualization (Matplotlib, Seaborn, Plotly)",
        "Pandas", "NumPy", "Data Preprocessing", "Feature Engineering",
        "Model Deployment", "Docker", "Git", "Cloud Platforms (AWS, Azure, GCP)",
        "Model Evaluation", "Experiment Tracking (MLflow, Weights & Biases)",
        "Power BI/Tableau"
    ],
}


def analyze_resume(_client_unused, resume_file, role, custom_jd, quick: bool = False):
    """Analyze resume locally using the ResumeAnalysisAgent (no backend)."""
    if not resume_file:
        st.error("Please upload a resume or select a saved resume.")
        return

    agent: ResumeAnalysisAgent = st.session_state.get("resume_agent")
    if not agent:
        st.error("Agent not initialized. Please configure provider/API key in the sidebar.")
        return

    with st.spinner("Analyzing resume locally..."):
        try:
            # If using a saved resume, fetch text from DB and analyze
            if resume_file == "USE_SAVED_RESUME":
                user = st.session_state.get("user") or {}
                resume_id = st.session_state.get("use_saved_resume_id") or st.session_state.get("selected_resume_id")
                if not (user and resume_id):
                    st.error("Could not determine saved resume to analyze.")
                    return
                row = get_user_resume_by_id(user.get("id"), resume_id)
                if not row or not row.get("resume_text"):
                    st.error("Saved resume not found or empty.")
                    return
                result = agent.analyze_resume_text(
                    row.get("resume_text", ""),
                    role_requirements=ROLE_REQUIREMENTS.get(role),
                    custom_jd=custom_jd,
                    quick=quick,
                )
            else:
                # Analyze uploaded file
                result = agent.analyze_resume(
                    resume_file,
                    role_requirements=ROLE_REQUIREMENTS.get(role),
                    custom_jd=custom_jd,
                    quick=quick,
                )
                # Save uploaded resume for reuse if user logged in
                user = st.session_state.get("user")
                if user and agent.resume_text and agent.resume_hash:
                    try:
                        filename = getattr(resume_file, "name", "resume")
                        rid = save_user_resume(user["id"], filename, agent.resume_hash, agent.resume_text)
                        if rid:
                            st.session_state["selected_resume_id"] = rid
                    except Exception as e:
                        st.info(f"Could not save resume to DB: {e}")

            st.session_state.resume_analyzed = True
            st.session_state.analysis_result = result
            return result
        except Exception as e:
            st.error(f"Error analyzing resume: {e}")


def render(client=None):
    role, custom_jd = ui.role_selection_section(ROLE_REQUIREMENTS) 
    # this will return selecteed role and jd 
    uploaded_resume = ui.resume_upload_section()
    # this will return uploaded resume

    quick_mode = st.checkbox(
        "Quick analysis (faster, fewer skills, skips deep weaknesses)",
        value=True,
        help="Quick mode avoids an extra JD skill extraction call and limits skills to speed up analysis.",
    )

    col = st.columns([1, 1, 1])
    with col[1]:
        if st.button("Analyze Resume", type="primary"):
            has_resume = uploaded_resume is not None
            if has_resume:
                result = analyze_resume(None, uploaded_resume, role, custom_jd, quick=quick_mode)
                if result:
                    st.session_state.analysis_result = result
                    st.session_state.resume_analyzed = True
                    if st.session_state.get('user'):
                        st.session_state.analysis_result['_user'] = st.session_state.user.get('username') or st.session_state.user.get('email')
                    st.rerun()
            else:
                if not has_resume:
                    st.warning("Please upload a resume or select a saved resume.")

    if st.session_state.analysis_result:
        ui.display_analysis_results(st.session_state.analysis_result)
