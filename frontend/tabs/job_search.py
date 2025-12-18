from frontend import ui

def render():
    import os
    import streamlit as st
    from agents import JobAgent

    st.title("🌍 Recruitment Agent - Job Search")

    _us = st.session_state.get('user_settings') or {}
    saved_jooble_key = _us.get('jooble_api_key') or os.getenv("JOOBLE_API_KEY")
    agent = JobAgent(jooble_api_key=saved_jooble_key)

    @st.cache_data(ttl=600, show_spinner=False)
    def _cached_job_search(platform: str, query: str, location: str | None, num_results: int, country: str, experience: int | None, jooble_key: str | None):
        ja = JobAgent(jooble_api_key=jooble_key)
        return ja.search_jobs(
            query=query,
            location=location,
            platform=platform.lower(),
            experience=experience,
            num_results=num_results,
            country=country,
            jooble_api_key=jooble_key,
        )

    platform = st.selectbox("Select Job Platform", ["Adzuna", "Jooble"])

    query = st.selectbox(
        "Select Role",
        [
            "Data Analyst", "Data Scientist", "Software Engineer", "ML Engineer",
            "Backend Developer", "Frontend Developer", "Full Stack Developer",
            "AI Engineer", "Business Analyst", "DevOps Engineer", "Cloud Engineer",
            "Cybersecurity Specialist", "Product Manager", "QA Engineer"
        ]
    )

    location = st.selectbox(
        "Enter Location (optional)",
        ["India", "Delhi", "Bengaluru", "Mumbai", "Hyderabad", "Chennai", "Pune", "Kolkata"]
    )

    country = "in"
    experience = 0
    num_results = st.slider("Number of Results", 5, 30, 10)

    if st.button("🔍 Search Jobs"):
        with st.spinner("Fetching jobs..."):
            jobs = _cached_job_search(platform, query, location, num_results, country, None, saved_jooble_key)

        if jobs and isinstance(jobs, list) and jobs and "error" not in jobs[0]:
            for job in jobs:
                st.markdown(f"### {job['title']}")
                st.write(f"**Company:** {job['company']}")
                st.write(f"**Location:** {job['location']}")
                st.markdown(f"[Apply Here]({job['link']})", unsafe_allow_html=True)
                st.markdown("---")
        else:
            msg = jobs[0].get("error") if isinstance(jobs, list) and jobs else "No jobs found."
            st.error(msg)
