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
from database import save_user_resume, get_user_resume_by_id, get_user_settings
from agents import ResumeAnalysisAgent
from utils.file_handlers import extract_text_from_file

router = APIRouter()


def get_user_agent(user: dict = Depends(verify_token)):
    """Get or create ResumeAnalysisAgent for user"""
    user_id = user["user_id"]
    
    # Get user settings
    settings = get_user_settings(user_id) or {}
    
    provider = settings.get("provider", "groq")
    api_key = settings.get("api_key", os.getenv("GROQ_API_KEY"))
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
        
        # Save to database
        resume_id = save_user_resume(user_id, resume_text, file.filename)
        
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
        if resume_id:
            resume_data = get_user_resume_by_id(resume_id, user_id)
        else:
            resume_data = get_user_resume_by_id(None, user_id)
        
        if not resume_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No resume found. Please upload a resume first."
            )
        
        resume_text = resume_data.get("resume_text")
        
        # Set resume text in agent
        agent.set_resume(resume_text)
        
        # Perform analysis
        result = agent.analyze_resume(
            role=request.role,
            cutoff_score=request.cutoff_score,
            jd_text=request.jd_text,
            custom_skills=request.custom_skills
        )
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Analysis failed"
            )
        
        return ResumeAnalysisResponse(
            overall_score=result.get("overall_score", 0),
            matching_skills=result.get("matching_skills", []),
            missing_skills=result.get("missing_skills", []),
            skill_scores=result.get("skill_scores", {}),
            strengths=result.get("strengths", []),
            weaknesses=result.get("weaknesses", []),
            recommendations=result.get("recommendations", []),
            resume_hash=result.get("resume_hash", "")
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Analysis failed: {str(e)}"
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
            resume_data = get_user_resume_by_id(resume_id, user_id)
        else:
            resume_data = get_user_resume_by_id(None, user_id)
        
        if not resume_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No resume found. Please upload a resume first."
            )
        
        resume_text = resume_data.get("resume_text")
        
        # Set resume text in agent
        if not agent.resume_text:
            agent.set_resume(resume_text)
        
        # Check if analysis exists
        if not agent.analysis_result:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Please analyze the resume first"
            )
        
        # Get improvements
        improvements = agent.generate_improvements(focus_areas=request.focus_areas)
        
        if not improvements:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to generate improvements"
            )
        
        return ResumeImprovementResponse(
            improved_sections=improvements.get("sections", {}),
            suggestions=improvements.get("suggestions", []),
            overall_improvements=improvements.get("summary", "")
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
            resume_data = get_user_resume_by_id(resume_id, user_id)
        else:
            resume_data = get_user_resume_by_id(None, user_id)
        
        if not resume_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No resume found. Please upload a resume first."
            )
        
        resume_text = resume_data.get("resume_text")
        
        # Set resume text in agent
        if not agent.resume_text:
            agent.set_resume(resume_text)
        
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
