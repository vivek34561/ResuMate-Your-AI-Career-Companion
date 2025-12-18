import os
import json
import streamlit as st
from frontend import ui
from agents import ResumeAnalysisAgent
from database import (
    save_user_resume,
    get_user_resume_by_id,
)

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


def analyze_resume(agent: ResumeAnalysisAgent, resume_file, role, custom_jd, quick: bool = False):
    if not resume_file:
        st.error("Please upload a resume or select a saved resume.")
        return

    with st.spinner("Quick analysis running..." if quick else "Analyzing resume... This may take a minute."):
        try:
            use_saved_resume_id = st.session_state.get('use_saved_resume_id')
            if resume_file == "USE_SAVED_RESUME" and use_saved_resume_id and st.session_state.get('user'):
                ur = get_user_resume_by_id(st.session_state.user['id'], use_saved_resume_id)
                if ur and ur.get('resume_text'):
                    result = agent.analyze_resume_text(
                        ur['resume_text'],
                        custom_jd=custom_jd if custom_jd else None,
                        role_requirements=ROLE_REQUIREMENTS.get(role) if not custom_jd else None,
                        quick=quick,
                    )
                else:
                    st.error("Saved resume not found. Please upload a new file.")
                    return
            else:
                result = agent.analyze_resume(
                    resume_file,
                    custom_jd=custom_jd if custom_jd else None,
                    role_requirements=ROLE_REQUIREMENTS.get(role) if not custom_jd else None,
                    quick=quick,
                )
            st.session_state.resume_analyzed = True
            st.session_state.analysis_result = result
            try:
                if st.session_state.user and getattr(agent, 'resume_text', None):
                    r_hash = getattr(agent, 'resume_hash', None)
                    if resume_file != "USE_SAVED_RESUME":
                        save_user_resume(
                            st.session_state.user['id'],
                            getattr(resume_file, 'name', 'uploaded_resume'),
                            r_hash,
                            agent.resume_text,
                        )
            except Exception as e:
                st.info(f"Saved analysis; resume cache note: {e}")
            return result
        except Exception as e:
            st.error(f"Error analyzing resume: {e}")


def render(agent: ResumeAnalysisAgent):
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
            if agent and has_resume:
                result = analyze_resume(agent, uploaded_resume, role, custom_jd, quick=quick_mode)
                if result:
                    st.session_state.analysis_result = result
                    st.session_state.resume_analyzed = True
                    st.session_state.analysis_result['_user'] = st.session_state.user['username'] if st.session_state.user else 'anonymous'
                    st.rerun()
            else:
                if not agent:
                    st.warning("Please configure your provider/API key in the sidebar.")
                elif not has_resume:
                    st.warning("Please upload a resume or select a saved resume.")

    if st.session_state.analysis_result:
        ui.display_analysis_results(st.session_state.analysis_result)
