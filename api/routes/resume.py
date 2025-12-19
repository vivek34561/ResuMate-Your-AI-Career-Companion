"""
Resume analysis API routes
"""

from fastapi import APIRouter, HTTPException, Depends, status, UploadFile, File, Form
from typing import Optional, List
import io
import os

from api.models import (
    ResumeUploadResponse,
    ResumeAnalysisRequest,
    ResumeAnalysisResponse,
    ResumeImprovementRequest,
    ResumeImprovementResponse,
    QuestionRequest,
    QuestionResponse,
    SuccessResponse,
)
from api.routes.auth import verify_token
from database import save_user_resume, get_user_resume_by_id, get_user_settings, get_user_resumes
import hashlib
from agents import ResumeAnalysisAgent
from utils.file_handlers import extract_text_from_file

router = APIRouter()

# Simple in-memory cache to allow improvement requests after analysis
# In production, replace with Redis or database persistence
user_analysis_cache = {}


def get_user_agent(user: dict = Depends(verify_token)):
    """Get or create ResumeAnalysisAgent for user"""
    user_id = user["user_id"]
    
    # Get user settings
    settings = get_user_settings(user_id) or {}
    
    provider = settings.get("provider", "groq")
    api_key = settings.get("api_key") or os.getenv("GROQ_API_KEY") or os.getenv("OPENAI_API_KEY")
    model = settings.get("model")
    ollama_base_url = settings.get("ollama_base_url", "http://localhost:11434")
    
    if not api_key and provider in ["openai", "groq"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"API key not configured for provider: {provider}"
        )
    
    agent = ResumeAnalysisAgent(
        api_key=api_key,
        provider=provider,
        model=model,
        ollama_base_url=ollama_base_url,
        user_id=user_id
    )
    
    return agent


@router.post("/upload", response_model=ResumeUploadResponse)
async def upload_resume(
    file: UploadFile = File(...),
    user: dict = Depends(verify_token)
):
    """
    Upload a resume file (PDF or TXT)
    
    - **file**: Resume file to upload
    
    Requires: Bearer token in Authorization header
    """
    try:
        user_id = user["user_id"]
        
        # Validate file type
        if not file.filename.lower().endswith(('.pdf', '.txt')):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only PDF and TXT files are supported"
            )
        
        # Read file content
        content = await file.read()
        file_obj = io.BytesIO(content)
        file_obj.name = file.filename
        
        # Extract text
        try:
            resume_text = extract_text_from_file(file_obj)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to extract text from file: {str(e)}"
            )
        
        if not resume_text or len(resume_text.strip()) < 50:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Resume text is too short or empty"
            )
        
        # Save to database (compute stable hash of content)
        resume_hash = hashlib.sha256(resume_text.encode("utf-8")).hexdigest()
        safe_name = file.filename or "uploaded_resume"
        resume_id = save_user_resume(user_id, safe_name, resume_hash, resume_text)
        
        if not resume_id:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to save resume"
            )
        
        # Return preview
        preview = resume_text[:500] + "..." if len(resume_text) > 500 else resume_text
        
        return ResumeUploadResponse(
            message="Resume uploaded successfully",
            resume_id=resume_id,
            text_preview=preview
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Upload failed: {str(e)}"
        )


@router.post("/analyze", response_model=ResumeAnalysisResponse)
async def analyze_resume(
    request: ResumeAnalysisRequest,
    resume_id: Optional[int] = None,
    agent: ResumeAnalysisAgent = Depends(get_user_agent),
    user: dict = Depends(verify_token)
):
    """
    Analyze resume against job requirements
    
    - **role**: Target job role
    - **cutoff_score**: Minimum score threshold (0-100)
    - **jd_text**: Optional job description text
    - **custom_skills**: Optional list of required skills
    - **resume_id**: Optional resume ID (uses latest if not provided)
    
    Requires: Bearer token in Authorization header
    """
    try:
        user_id = user["user_id"]
        
        # Get resume text
        """
        Deprecated: FastAPI backend removed. This module is no longer used.
        """

        raise RuntimeError("FastAPI routes removed. Use Streamlit-only frontend.")
            overall_score=result.get("overall_score", 0),
            matching_skills=result.get("matching_skills", []),
            missing_skills=result.get("missing_skills", []),
            skill_scores=result.get("skill_scores", {}),
            strengths=result.get("strengths", []),
            weaknesses=result.get("weaknesses", []),
            recommendations=result.get("recommendations", []),
            resume_hash=result.get("resume_hash", "")
        )
        # cache analysis for subsequent improvement calls
        try:
            user_analysis_cache[user_id] = {
                "resume_text": resume_text,
                "analysis": result,
            }
        except Exception:
            pass
        return resp
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Analysis failed: {str(e)}"
        )

# Alias with trailing slash to avoid client path mismatch
router.add_api_route(
    "/analyze/",
    analyze_resume,
    methods=["POST"],
    response_model=ResumeAnalysisResponse,
)


@router.post("/improve", response_model=ResumeImprovementResponse)
async def improve_resume(
    request: ResumeImprovementRequest,
    resume_id: Optional[int] = None,
    agent: ResumeAnalysisAgent = Depends(get_user_agent),
    user: dict = Depends(verify_token)
):
    """
    Get resume improvement suggestions
    
    - **focus_areas**: Optional list of areas to focus on
    - **resume_id**: Optional resume ID (uses latest if not provided)
    
    Requires: Bearer token in Authorization header
    """
    try:
        user_id = user["user_id"]
        
        # Get resume text
        if resume_id:
            resume_data = get_user_resume_by_id(user_id, resume_id)
        else:
            all_resumes = get_user_resumes(user_id)
            if not all_resumes:
                resume_data = None
            else:
                latest_id = (all_resumes[0].get("id") if isinstance(all_resumes[0], dict) else all_resumes[0])
                resume_data = get_user_resume_by_id(user_id, latest_id)
        
        if not resume_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No resume found. Please upload a resume first."
            )
        
        resume_text = resume_data.get("resume_text")
        
        # Ensure agent has resume text
        if not agent.resume_text:
            agent.resume_text = resume_text
        
        # Ensure analysis exists: use cached analysis if available
        if not agent.analysis_result:
            cached = user_analysis_cache.get(user_id)
            if cached and cached.get("resume_text") == resume_text:
                agent.analysis_result = cached.get("analysis")
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Please analyze the resume first"
                )
        
        # Get improvements using improver agent
        improvements = agent.improve_resume(improvement_areas=(request.focus_areas or []), target_role="")
        
        if not improvements:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to generate improvements"
            )
        
        # Adapt improver output to response schema
        improved_sections = {}
        suggestions = []
        for area, data in (improvements or {}).items():
            if isinstance(data, dict):
                desc = data.get("description")
                if desc:
                    improved_sections[area] = desc
                for s in data.get("specific", []) or []:
                    suggestions.append(s)
        summary = "; ".join([f"{k}: {v[:80]}" for k, v in improved_sections.items()]) if improved_sections else ""
        return ResumeImprovementResponse(
            improved_sections=improved_sections,
            suggestions=suggestions,
            overall_improvements=summary
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Improvement generation failed: {str(e)}"
        )


@router.post("/ask", response_model=QuestionResponse)
async def ask_question(
    request: QuestionRequest,
    resume_id: Optional[int] = None,
    agent: ResumeAnalysisAgent = Depends(get_user_agent),
    user: dict = Depends(verify_token)
):
    """
    Ask questions about the resume using RAG
    
    - **question**: Question to ask
    - **chat_history**: Optional conversation history
    - **resume_id**: Optional resume ID (uses latest if not provided)
    
    Requires: Bearer token in Authorization header
    """
    try:
        user_id = user["user_id"]
        
        # Get resume text
        if resume_id:
            resume_data = get_user_resume_by_id(user_id, resume_id)
        else:
            all_resumes = get_user_resumes(user_id)
            if not all_resumes:
                resume_data = None
            else:
                latest_id = (all_resumes[0].get("id") if isinstance(all_resumes[0], dict) else all_resumes[0])
                resume_data = get_user_resume_by_id(user_id, latest_id)
        
        if not resume_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No resume found. Please upload a resume first."
            )
        
        resume_text = resume_data.get("resume_text")
        
        # Ensure agent has resume text
        if not agent.resume_text:
            agent.resume_text = resume_text
        
        # Ask question
        answer = agent.ask_question(request.question, request.chat_history)
        
        return QuestionResponse(
            answer=answer,
            context_used=True
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Question answering failed: {str(e)}"
        )


@router.get("/resumes")
async def list_resumes(user: dict = Depends(verify_token)):
    """
    Get list of user's uploaded resumes
    
    Requires: Bearer token in Authorization header
    """
    try:
        user_id = user["user_id"]
        
        # Get all resumes for user (you may need to add this function to database.py)
        # For now, return placeholder
        return {
            "message": "Resume list endpoint",
            "user_id": user_id
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch resumes: {str(e)}"
        )
