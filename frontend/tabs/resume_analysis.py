import os
import json
import streamlit as st
from frontend import ui
from frontend.backend_client import BackendClient

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


def analyze_resume(client: BackendClient, resume_file, role, custom_jd, quick: bool = False):
    if not resume_file:
        st.error("Please upload a resume or select a saved resume.")
        return

    with st.spinner("Analyzing resume via backend..."):
        try:
            active_resume_id = None
            # If using saved resume selected from sidebar
            if resume_file == "USE_SAVED_RESUME":
                active_resume_id = st.session_state.get("use_saved_resume_id") or st.session_state.get("selected_resume_id")
            else:
                # Upload new resume to backend
                upload_resp = client.upload_resume(st.session_state.get('user') or {}, resume_file)
                active_resume_id = upload_resp.get("resume_id")
                st.session_state["active_resume_id"] = active_resume_id

            if not active_resume_id:
                st.error("Could not determine resume to analyze.")
                return

            # Choose skills if no JD provided
            custom_skills = None if custom_jd else ROLE_REQUIREMENTS.get(role)
            result = client.analyze_resume(
                user=st.session_state.get('user') or {},
                role=role,
                jd_text=custom_jd or None,
                custom_skills=custom_skills,
                resume_id=active_resume_id,
                cutoff_score=75,
            )
            st.session_state.resume_analyzed = True
            st.session_state.analysis_result = result
            return result
        except Exception as e:
            st.error(f"Error analyzing resume: {e}")


def render(client: BackendClient):
    role, custom_jd = ui.role_selection_section(ROLE_REQUIREMENTS)
    uploaded_resume = ui.resume_upload_section()

    quick_mode = st.checkbox(
        "Quick analysis (faster, fewer skills, skips deep weaknesses)",
        value=True,
        help="Quick mode avoids an extra JD skill extraction call and limits skills to speed up analysis.",
    )

    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("Analyze Resume", type="primary"):
            has_resume = uploaded_resume is not None
            if client and has_resume:
                result = analyze_resume(client, uploaded_resume, role, custom_jd, quick=quick_mode)
                if result:
                    st.session_state.analysis_result = result
                    st.session_state.resume_analyzed = True
                    if st.session_state.get('user'):
                        st.session_state.analysis_result['_user'] = st.session_state.user.get('username') or st.session_state.user.get('email')
                    st.rerun()
            else:
                if not client:
                    st.warning("Backend client is not available.")
                elif not has_resume:
                    st.warning("Please upload a resume or select a saved resume.")

    if st.session_state.analysis_result:
        ui.display_analysis_results(st.session_state.analysis_result)
