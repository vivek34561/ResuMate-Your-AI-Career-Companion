"""
Mock Interview API routes
"""

from fastapi import APIRouter, HTTPException, Depends, status, UploadFile, File
from typing import Optional, Dict, Any
import time
import uuid
import os

from api.models import (
    InterviewStartRequest,
    InterviewStartResponse,
    InterviewQuestion,
    AnswerSubmission,
    AnswerSubmissionResponse,
    AnswerScore,
    InterviewSummaryRequest,
    InterviewSummary,
    SuccessResponse,
)
from api.routes.auth import verify_token
from api.routes.resume import get_user_agent
from database import get_user_resume_by_id
from agents import ResumeAnalysisAgent

router = APIRouter()

# In-memory storage for active interviews (use Redis in production)
active_interviews: Dict[str, Dict[str, Any]] = {}


@router.post("/start", response_model=InterviewStartResponse)
async def start_interview(
    request: InterviewStartRequest,
    resume_id: Optional[int] = None,
    agent: ResumeAnalysisAgent = Depends(get_user_agent),
    user: dict = Depends(verify_token)
):
    """
    Start a new mock interview
    
    - **question_types**: List of question types (Technical, Behavioral, etc.)
    - **difficulty**: Difficulty level (Easy, Medium, Hard)
    - **num_questions**: Number of questions (1-20)
    - **max_duration_minutes**: Maximum interview duration
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
        
        # Generate interview questions
        questions = agent.generate_interview_questions(
            question_types=[qt.value for qt in request.question_types],
            difficulty=request.difficulty.value,
            num_questions=request.num_questions
        )
        
        if not questions:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to generate interview questions"
            )
        
        # Normalize questions to list of strings
        normalized_questions = []
        for q in questions:
            if isinstance(q, dict):
                normalized_questions.append(q.get("question") or q.get("text") or str(q))
            else:
                normalized_questions.append(str(q))
        
        # Create interview session
        interview_id = str(uuid.uuid4())
        start_time = time.time()
        
        interview_session = {
            "interview_id": interview_id,
            "user_id": user_id,
            "resume_text": resume_text,
            "questions": normalized_questions[:request.num_questions],
            "question_types": [qt.value for qt in request.question_types],
            "difficulty": request.difficulty.value,
            "current_question": 0,
            "answers": [],
            "transcripts": [],
            "scores": [],
            "start_time": start_time,
            "max_duration_seconds": request.max_duration_minutes * 60,
            "completed": False,
        }
        
        active_interviews[interview_id] = interview_session
        
        # Format response
        question_list = [
            InterviewQuestion(
                question_id=i,
                question_text=q,
                question_type=request.question_types[i % len(request.question_types)]
            )
            for i, q in enumerate(normalized_questions[:request.num_questions])
        ]
        
        return InterviewStartResponse(
            interview_id=interview_id,
            questions=question_list,
            max_duration_seconds=interview_session["max_duration_seconds"],
            start_time=interview_session["start_time"]
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start interview: {str(e)}"
        )


@router.post("/answer", response_model=AnswerSubmissionResponse)
async def submit_answer(
    interview_id: str,
    answer: AnswerSubmission,
    agent: ResumeAnalysisAgent = Depends(get_user_agent),
    user: dict = Depends(verify_token)
):
    """
    Submit an answer to an interview question
    
    - **interview_id**: Interview session ID
    - **question_id**: Question ID being answered
    - **transcript**: Answer transcript text
    - **audio_duration**: Optional audio duration in seconds
    
    Requires: Bearer token in Authorization header
    """
    try:
        user_id = user["user_id"]
        
        # Get interview session
        if interview_id not in active_interviews:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Interview session not found"
            )
        
        session = active_interviews[interview_id]
        
        # Verify user owns this interview
        if session["user_id"] != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        # Check if interview is completed
        if session["completed"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Interview already completed"
            )
        
        # Check timeout
        elapsed = time.time() - session["start_time"]
        if elapsed > session["max_duration_seconds"]:
            session["completed"] = True
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Interview time limit exceeded"
            )
        
        # Validate question ID
        if answer.question_id >= len(session["questions"]):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid question ID"
            )
        
        # Get question
        question = session["questions"][answer.question_id]
        
        # Score the answer
        scores = agent.score_answer(question, answer.transcript)
        
        if not scores:
            # Provide default scores if scoring fails
            scores = {
                "communication": 5.0,
                "technical_knowledge": 5.0,
                "problem_solving": 5.0,
                "overall": 5.0,
                "feedback": "Unable to score answer automatically."
            }
        
        # Save answer and scores
        session["answers"].append(answer.transcript)
        session["transcripts"].append(answer.transcript)
        session["scores"].append(scores)
        session["current_question"] = answer.question_id + 1
        
        # Check if this was the last question
        next_question_id = None
        follow_up = None
        
        if session["current_question"] < len(session["questions"]):
            next_question_id = session["current_question"]
            
            # Generate follow-up question (optional)
            try:
                follow_up = agent.generate_followup_question(
                    last_question=question,
                    transcript=answer.transcript
                )
            except:
                pass
        else:
            # Mark as completed
            session["completed"] = True
        
        # Format response
        answer_score = AnswerScore(
            communication=scores.get("communication", 5.0),
            technical_knowledge=scores.get("technical_knowledge", 5.0),
            problem_solving=scores.get("problem_solving", 5.0),
            overall=scores.get("overall", 5.0),
            feedback=scores.get("feedback", "Good answer!")
        )
        
        return AnswerSubmissionResponse(
            question_id=answer.question_id,
            scores=answer_score,
            next_question_id=next_question_id,
            follow_up_question=follow_up
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to submit answer: {str(e)}"
        )


@router.post("/summary", response_model=InterviewSummary)
async def get_interview_summary(
    request: InterviewSummaryRequest,
    agent: ResumeAnalysisAgent = Depends(get_user_agent),
    user: dict = Depends(verify_token)
):
    """
    Get summary and evaluation of completed interview
    
    - **interview_id**: Interview session ID
    
    Requires: Bearer token in Authorization header
    """
    try:
        user_id = user["user_id"]
        interview_id = request.interview_id
        
        # Get interview session
        if interview_id not in active_interviews:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Interview session not found"
            )
        
        session = active_interviews[interview_id]
        
        # Verify user owns this interview
        if session["user_id"] != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        # Calculate average scores
        scores = session["scores"]
        
        if not scores:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No answers submitted yet"
            )
        
        avg_communication = sum(s.get("communication", 0) for s in scores) / len(scores)
        avg_technical = sum(s.get("technical_knowledge", 0) for s in scores) / len(scores)
        avg_problem_solving = sum(s.get("problem_solving", 0) for s in scores) / len(scores)
        overall_score = sum(s.get("overall", 0) for s in scores) / len(scores)
        
        # Determine decision
        if overall_score >= 7.5:
            decision = "Strong Hire"
        elif overall_score >= 6.0:
            decision = "Hire"
        elif overall_score >= 5.0:
            decision = "Maybe"
        else:
            decision = "No Hire"
        
        # Generate detailed feedback
        detailed_feedback = f"Overall performance was {'excellent' if overall_score >= 7.5 else 'good' if overall_score >= 6.0 else 'satisfactory' if overall_score >= 5.0 else 'needs improvement'}. "
        detailed_feedback += f"Communication skills scored {avg_communication:.1f}/10, technical knowledge scored {avg_technical:.1f}/10, and problem-solving scored {avg_problem_solving:.1f}/10."
        
        # Identify strengths and areas for improvement
        strengths = []
        improvements = []
        
        if avg_communication >= 7.0:
            strengths.append("Strong communication skills")
        elif avg_communication < 5.0:
            improvements.append("Communication clarity and articulation")
        
        if avg_technical >= 7.0:
            strengths.append("Solid technical knowledge")
        elif avg_technical < 5.0:
            improvements.append("Technical depth and understanding")
        
        if avg_problem_solving >= 7.0:
            strengths.append("Good problem-solving approach")
        elif avg_problem_solving < 5.0:
            improvements.append("Problem-solving methodology")
        
        return InterviewSummary(
            total_questions=len(session["questions"]),
            answered_questions=len(scores),
            average_communication=avg_communication,
            average_technical=avg_technical,
            average_problem_solving=avg_problem_solving,
            overall_score=overall_score,
            decision=decision,
            detailed_feedback=detailed_feedback,
            strengths=strengths,
            areas_for_improvement=improvements
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate summary: {str(e)}"
        )


@router.get("/active")
async def get_active_interviews(user: dict = Depends(verify_token)):
    """
    Get list of active interviews for current user
    
    Requires: Bearer token in Authorization header
    """
    try:
        user_id = user["user_id"]
        
        # Filter interviews for this user
        user_interviews = []
        for interview_id, session in active_interviews.items():
            if session["user_id"] == user_id:
                user_interviews.append({
                    "interview_id": interview_id,
                    "start_time": session["start_time"],
                    "total_questions": len(session["questions"]),
                    "answered_questions": len(session["scores"]),
                    "completed": session["completed"]
                })
        
        return {
            "interviews": user_interviews,
            "count": len(user_interviews)
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch interviews: {str(e)}"
        )


@router.delete("/{interview_id}")
async def delete_interview(
    interview_id: str,
    user: dict = Depends(verify_token)
):
    """
    Delete an interview session
    
    - **interview_id**: Interview session ID
    
    Requires: Bearer token in Authorization header
    """
    try:
        user_id = user["user_id"]
        
        if interview_id not in active_interviews:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Interview session not found"
            )
        
        session = active_interviews[interview_id]
        
        # Verify user owns this interview
        if session["user_id"] != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        # Delete session
        del active_interviews[interview_id]
        
        return SuccessResponse(
            success=True,
            message="Interview session deleted successfully"
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete interview: {str(e)}"
        )
