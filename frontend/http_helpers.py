import os
import time
import jwt
from typing import Any, Dict, Optional


def base_url() -> str:
    return (os.getenv("BACKEND_URL") or "http://localhost:8000").rstrip("/")


def auth_headers(user: Optional[Dict[str, Any]], extra: Optional[Dict[str, str]] = None) -> Dict[str, str]:
    headers = {"Accept": "application/json"} 
    if extra:
        headers.update(extra)
    if not user:
        return headers
    secret = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
    payload = {
        "user_id": user.get("id") or user.get("user_id"),
        "email": user.get("email") or "user@example.com",
        "exp": int(time.time()) + 3600,
    }
    token = jwt.encode(payload, secret, algorithm="HS256")
    headers["Authorization"] = f"Bearer {token}"
    return headers
