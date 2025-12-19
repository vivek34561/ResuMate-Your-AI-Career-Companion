"""
DEPRECATED MODULE
This module is no longer used. The app is Streamlit-only and calls local
agents directly (no FastAPI backend).

It is kept temporarily to avoid import errors during transition.
Any import or usage will raise a clear error with migration guidance.
"""

class BackendClient:  # noqa: N801
    def __init__(self, *_, **__):  # pragma: no cover
        raise RuntimeError(
            "frontend/backend_client.py is deprecated. FastAPI backend removed. "
            "Use local agents via st.session_state.resume_agent (see frontend/provider.py)."
        )

__all__ = ["BackendClient"]
