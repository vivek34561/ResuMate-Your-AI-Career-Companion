import streamlit as st
from frontend import ui
from frontend.backend_client import BackendClient


def improve_resume(client: BackendClient, improvement_areas: list, target_role: str):
    try:
        resume_id = st.session_state.get("active_resume_id") or st.session_state.get("use_saved_resume_id") or st.session_state.get("selected_resume_id")
        resp = client.improve_resume(st.session_state.get('user') or {}, focus_areas=improvement_areas, resume_id=resume_id)
        # Adapt backend response to UI-expected structure
        improved_sections = resp.get("improved_sections", {})
        suggestions = resp.get("suggestions", [])
        adapted = {}
        for section, text in improved_sections.items():
            adapted[section] = {
                "description": text,
                "specific": suggestions or [],
            }
        if not adapted:
            st.warning("⚠️ No specific improvements returned. Try selecting different areas or re-running analysis.")
        return adapted
    except Exception as e:
        st.error(f"Error generating improvement suggestions: {e}")
        return {}


def get_improved_resume(client: BackendClient, target_role: str, highlight_skills: str):
    # Not yet implemented on backend; fallback to suggestions summary
    try:
        sugg = st.session_state.get('improvement_suggestions') or {}
        combined = []
        for k, v in sugg.items():
            if isinstance(v, dict):
                desc = v.get('description')
                if desc:
                    combined.append(f"[{k}] {desc}")
                for s in v.get('specific', []) or []:
                    combined.append(f"- {s}")
            else:
                combined.append(str(v))
        if not combined:
            return "No improved resume text available. Generate suggestions first."
        return "\n".join(combined)
    except Exception:
        return "Error generating improved resume."


def render(client: BackendClient):
    if st.session_state.resume_analyzed and client:
        ui.resume_improvement_section(
            has_resume=True,
            improve_resume_func=lambda areas, role: improve_resume(client, areas, role),
            get_improved_resume_func=lambda role, skills: get_improved_resume(client, role, skills),
        )
    else:
        st.warning("Please upload and analyze a resume first in the 'Resume Analysis' tab.")
