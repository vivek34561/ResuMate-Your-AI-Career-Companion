from typing import Callable
import streamlit as st


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
