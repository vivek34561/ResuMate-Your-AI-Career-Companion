from typing import Callable
import streamlit as st


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
                        original_text = getattr(st.session_state.get('resume_agent'), 'resume_text', None)
                        # Gracefully handle None or non-string values
                        if not isinstance(original_text, str):
                            original_text = original_text or "Original resume not available"
                        st.text_area(
                            "Original",
                            value=original_text[:2000] if len(original_text) > 2000 else original_text,
                            height=400,
                            disabled=True,
                            key="original_resume_view",
                        )
                        if isinstance(original_text, str) and len(original_text) > 2000:
                            st.caption("📝 Showing first 2000 characters")
                    with col_new:
                        st.markdown("#### ✨ Improved Resume")
                        improved_text = st.session_state.get('improved_resume_text') or ""
                        st.text_area(
                            "Improved",
                            value=improved_text[:2000] if len(improved_text) > 2000 else improved_text,
                            height=400,
                            disabled=True,
                            key="improved_resume_compare_view",
                        )
                        if len(improved_text) > 2000:
                            st.caption("📝 Showing first 2000 characters")
                    st.success("✅ Notice the improvements: stronger action verbs, quantified achievements, better keywords, and ATS optimization!")
    else:
        st.warning("Please upload and analyze a resume first in the 'Resume Analysis' tab.")
