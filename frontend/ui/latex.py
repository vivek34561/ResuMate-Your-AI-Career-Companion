from typing import Callable
import streamlit as st


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
