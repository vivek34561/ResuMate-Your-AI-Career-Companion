from frontend import ui
from frontend.backend_client import BackendClient

def render(client: BackendClient):
    import streamlit as st

    st.title("🌍 Recruitment Agent - Job Search")

    @st.cache_data(ttl=600, show_spinner=False)
    def _cached_job_search(platform: str, query: str, location: str | None, num_results: int):
        return client.search_jobs(
            user=st.session_state.get('user') or {},
            platform=platform.lower(),
            query=query,
            location=location,
            max_results=num_results,
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

    num_results = st.slider("Number of Results", 5, 30, 10)

    if st.button("🔍 Search Jobs"):
        with st.spinner("Fetching jobs..."):
            jobs = _cached_job_search(platform, query, location, num_results)

        if jobs and isinstance(jobs, list):
            if len(jobs) == 0:
                st.info("No jobs found.")
            for job in jobs:
                title = job.get('title') or 'Untitled'
                company = job.get('company') or 'Unknown'
                loc = job.get('location') or ''
                link = job.get('url') or job.get('link') or '#'
                st.markdown(f"### {title}")
                st.write(f"**Company:** {company}")
                st.write(f"**Location:** {loc}")
                if link and link != '#':
                    st.markdown(f"[Apply Here]({link})", unsafe_allow_html=True)
                st.markdown("---")
        else:
            st.error("No jobs found or an error occurred.")
