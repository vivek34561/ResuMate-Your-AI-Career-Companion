from typing import Dict
import streamlit as st


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
                        'bordercolor': "gray"},
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

    # Enhanced Visuals (radar, pie, ranking, waterfall)
    try:
        from utils.visualizations import display_enhanced_visualizations
        display_enhanced_visualizations(analysis_result)
    except Exception as _e:
        # Keep UI resilient if optional visuals fail
        pass
