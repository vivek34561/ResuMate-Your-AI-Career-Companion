import os
import sys
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Ensure project root is on sys.path so `api` package is importable
CURRENT_DIR = os.path.dirname(__file__)
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, os.pardir))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# Reuse existing API routers
from api.routes import auth as auth_routes
from api.routes import resume as resume_routes
from api.routes import settings as settings_routes
from api.routes import interview as interview_routes
from api.routes import jobs as jobs_routes


def create_app() -> FastAPI:
    # Load environment variables from .env so backend can access API keys
    try:
        load_dotenv()
    except Exception:
        pass
    app = FastAPI(
        title="ResuMate Backend",
        version="1.0.0",
        description="FastAPI backend for ResuMate"
    )

    # CORS for Streamlit (localhost:8501 by default)
    allowed_origins = os.getenv("CORS_ALLOWED_ORIGINS", "http://localhost:8501,https://localhost:8501").split(",")
    allowed_origins = [o.strip() for o in allowed_origins if o.strip()]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins or ["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Health check
    @app.get("/health")
    def health():
        return {"status": "ok"}

    # Mount routers with versioned prefix
    app.include_router(auth_routes.router, prefix="/api/v1/auth", tags=["auth"]) 
    app.include_router(settings_routes.router, prefix="/api/v1/settings", tags=["settings"]) 
    app.include_router(resume_routes.router, prefix="/api/v1/resume", tags=["resume"]) 
    app.include_router(interview_routes.router, prefix="/api/v1/interview", tags=["interview"]) 
    app.include_router(jobs_routes.router, prefix="/api/v1/jobs", tags=["jobs"]) 

    # Debug: log registered routes on startup
    try:
        print("[ResuMate] Registered routes:")
        for r in app.routes:
            methods = getattr(r, "methods", None)
            path = getattr(r, "path", None)
            if methods and path:
                print(f"  {sorted(list(methods))} -> {path}")
    except Exception:
        pass

    return app


app = create_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend.main:app",
        host=os.getenv("BACKEND_HOST", "0.0.0.0"),
        port=int(os.getenv("BACKEND_PORT", "8000")),
        reload=True,
    )
