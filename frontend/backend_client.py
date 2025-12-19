import os
import time
import jwt
import requests
from typing import Any, Dict, List, Optional

DEFAULT_TIMEOUT = 30


class BackendClient:
    def __init__(self, base_url: Optional[str] = None):
        self.base_url = (base_url or os.getenv("BACKEND_URL") or "http://localhost:8000").rstrip("/")
        self.secret = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")

    def _make_token(self, user: Optional[Dict[str, Any]]) -> Optional[str]:
        if not user:
            return None
        payload = {
            "user_id": user.get("id") or user.get("user_id"),
            "email": user.get("email") or "user@example.com",
            "exp": int(time.time()) + 3600,
        }
        return jwt.encode(payload, self.secret, algorithm="HS256")

    def _headers(self, user: Optional[Dict[str, Any]] = None, extra: Optional[Dict[str, str]] = None) -> Dict[str, str]:
        h = {"Accept": "application/json"}
        if extra:
            h.update(extra)
        token = self._make_token(user)
        if token:
            h["Authorization"] = f"Bearer {token}"
        return h

    def health(self) -> bool:
        try:
            r = requests.get(f"{self.base_url}/health", timeout=5)
            return r.ok and (r.json() or {}).get("status") == "ok"
        except Exception:
            return False

    # Settings
    def get_settings(self, user: Dict[str, Any]) -> Dict[str, Any]:
        r = requests.get(
            f"{self.base_url}/api/v1/settings/",
            headers=self._headers(user),
            timeout=DEFAULT_TIMEOUT,
        )
        r.raise_for_status()
        return r.json()

    def update_settings(self, user: Dict[str, Any], payload: Dict[str, Any]) -> Dict[str, Any]:
        r = requests.put(
            f"{self.base_url}/api/v1/settings/",
            headers=self._headers(user, {"Content-Type": "application/json"}),
            json=payload,
            timeout=DEFAULT_TIMEOUT,
        )
        r.raise_for_status()
        return r.json()

    # Resume
    def upload_resume(self, user: Dict[str, Any], file_obj) -> Dict[str, Any]:
        files = {"file": (getattr(file_obj, "name", "resume.pdf"), file_obj, getattr(file_obj, "type", "application/octet-stream"))}
        r = requests.post(
            f"{self.base_url}/api/v1/resume/upload",
            headers=self._headers(user),
            files=files,
            timeout=DEFAULT_TIMEOUT,
        )
        r.raise_for_status()
        return r.json()

    def analyze_resume(
        self,
        user: Dict[str, Any],
        role: str,
        jd_text: Optional[str] = None,
        custom_skills: Optional[List[str]] = None,
        resume_id: Optional[int] = None,
        cutoff_score: int = 75,
    ) -> Dict[str, Any]:
        payload = {
            "role": role,
            "cutoff_score": cutoff_score,
            "jd_text": jd_text,
            "custom_skills": custom_skills,
        }
        params = {}
        if resume_id is not None:
            params["resume_id"] = resume_id
        r = requests.post(
            f"{self.base_url}/api/v1/resume/analyze/",
            headers=self._headers(user, {"Content-Type": "application/json"}),
            json=payload,
            params=params,
            timeout=DEFAULT_TIMEOUT,
        )
        r.raise_for_status()
        return r.json()

    def ask_question(
        self,
        user: Dict[str, Any],
        question: str,
        chat_history: Optional[List[Dict[str, str]]] = None,
        resume_id: Optional[int] = None,
    ) -> Dict[str, Any]:
        payload = {"question": question, "chat_history": chat_history or []}
        params = {}
        if resume_id is not None:
            params["resume_id"] = resume_id
        r = requests.post(
            f"{self.base_url}/api/v1/resume/ask",
            headers=self._headers(user, {"Content-Type": "application/json"}),
            json=payload,
            params=params,
            timeout=DEFAULT_TIMEOUT,
        )
        r.raise_for_status()
        return r.json()

    def improve_resume(self, user: Dict[str, Any], focus_areas: Optional[List[str]] = None, resume_id: Optional[int] = None) -> Dict[str, Any]:
        payload = {"focus_areas": focus_areas or []}
        params = {}
        if resume_id is not None:
            params["resume_id"] = resume_id
        r = requests.post(
            f"{self.base_url}/api/v1/resume/improve",
            headers=self._headers(user, {"Content-Type": "application/json"}),
            json=payload,
            params=params,
            timeout=DEFAULT_TIMEOUT,
        )
        r.raise_for_status()
        return r.json()

    # Interview
    def generate_interview_questions(
        self,
        user: Dict[str, Any],
        question_types: List[str],
        difficulty: str,
        num_questions: int,
        resume_id: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        payload = {
            "question_types": question_types,
            "difficulty": difficulty,
            "num_questions": num_questions,
        }
        params = {}
        if resume_id is not None:
            params["resume_id"] = resume_id
        r = requests.post(
            f"{self.base_url}/api/v1/interview/questions",
            headers=self._headers(user, {"Content-Type": "application/json"}),
            json=payload,
            params=params,
            timeout=DEFAULT_TIMEOUT,
        )
        r.raise_for_status()
        data = r.json() or {}
        return data.get("questions", [])

    # Jobs
    def search_jobs(
        self,
        user: Dict[str, Any],
        platform: str,
        query: Optional[str],
        location: Optional[str],
        max_results: int = 10,
    ) -> List[Dict[str, Any]]:
        payload = {
            "query": query,
            "location": location,
            "max_results": max_results,
        }
        r = requests.post(
            f"{self.base_url}/api/v1/jobs/search",
            headers=self._headers(user, {"Content-Type": "application/json"}),
            json=payload,
            params={"platform": platform},
            timeout=DEFAULT_TIMEOUT,
        )
        r.raise_for_status()
        data = r.json() or {}
        return data.get("jobs", [])
