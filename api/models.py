"""
Pydantic models for API request/response validation
"""

from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


# Enums
class DifficultyLevel(str, Enum):
    EASY = "Easy"
    MEDIUM = "Medium"
    HARD = "Hard"


class QuestionType(str, Enum):
    TECHNICAL = "Technical"
    BEHAVIORAL = "Behavioral"
    SYSTEM_DESIGN = "System Design"
    CODING = "Coding"


class LLMProvider(str, Enum):
    OPENAI = "openai"
    GROQ = "groq"
    OLLAMA = "ollama"


# Auth Models
class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
    full_name: Optional[str] = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: int
    email: str


class GoogleAuthRequest(BaseModel):
    google_id: str
    email: EmailStr
    name: str
    picture: Optional[str] = None


# User Models
class UserSettings(BaseModel):
    provider: LLMProvider = LLMProvider.GROQ
    api_key: Optional[str] = None
    model: Optional[str] = None
    ollama_base_url: Optional[str] = "http://localhost:11434"
    ollama_model: Optional[str] = "llama3.1:8b"


class UserSettingsUpdate(BaseModel):
    provider: Optional[LLMProvider] = None
    api_key: Optional[str] = None
    model: Optional[str] = None
    ollama_base_url: Optional[str] = None
    ollama_model: Optional[str] = None


# Resume Models
class ResumeUploadResponse(BaseModel):
    message: str
    resume_id: int
    text_preview: str


class ResumeAnalysisRequest(BaseModel):
    role: str
    cutoff_score: int = Field(default=75, ge=0, le=100)
    jd_text: Optional[str] = None
    custom_skills: Optional[List[str]] = None


class SkillScore(BaseModel):
    skill: str
    score: float
    present: bool


class ResumeAnalysisResponse(BaseModel):
    overall_score: float
    matching_skills: List[str]
    missing_skills: List[str]
    skill_scores: Dict[str, float]
    strengths: List[str]
    weaknesses: List[Dict[str, Any]]
    recommendations: List[str]
    resume_hash: str


class ResumeImprovementRequest(BaseModel):
    focus_areas: Optional[List[str]] = None


class ResumeImprovementResponse(BaseModel):
    improved_sections: Dict[str, str]
    suggestions: List[str]
    overall_improvements: str


# Interview Models
class InterviewStartRequest(BaseModel):
    question_types: List[QuestionType]
    difficulty: DifficultyLevel
    num_questions: int = Field(default=10, ge=1, le=20)
    max_duration_minutes: int = Field(default=15, ge=5, le=60)


class InterviewQuestion(BaseModel):
    question_id: int
    question_text: str
    question_type: QuestionType


class InterviewStartResponse(BaseModel):
    interview_id: str
    questions: List[InterviewQuestion]
    max_duration_seconds: int
    start_time: datetime


class AnswerSubmission(BaseModel):
    question_id: int
    transcript: str
    audio_duration: Optional[float] = None


class AnswerScore(BaseModel):
    communication: float = Field(..., ge=0, le=10)
    technical_knowledge: float = Field(..., ge=0, le=10)
    problem_solving: float = Field(..., ge=0, le=10)
    overall: float = Field(..., ge=0, le=10)
    feedback: str


class AnswerSubmissionResponse(BaseModel):
    question_id: int
    scores: AnswerScore
    next_question_id: Optional[int] = None
    follow_up_question: Optional[str] = None


class InterviewSummaryRequest(BaseModel):
    interview_id: str


class InterviewSummary(BaseModel):
    total_questions: int
    answered_questions: int
    average_communication: float
    average_technical: float
    average_problem_solving: float
    overall_score: float
    decision: str
    detailed_feedback: str
    strengths: List[str]
    areas_for_improvement: List[str]


# Q&A Models
class QuestionRequest(BaseModel):
    question: str
    chat_history: Optional[List[Dict[str, str]]] = []


class QuestionResponse(BaseModel):
    answer: str
    context_used: bool


# Job Search Models
class JobSearchRequest(BaseModel):
    query: Optional[str] = None
    location: Optional[str] = None
    max_results: int = Field(default=10, ge=1, le=50)


class JobListing(BaseModel):
    title: str
    company: str
    location: str
    description: str
    url: Optional[str] = None
    posted_date: Optional[str] = None


class JobSearchResponse(BaseModel):
    jobs: List[JobListing]
    total_found: int


# Response Models
class SuccessResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Any] = None


class ErrorResponse(BaseModel):
    success: bool = False
    error: str
    detail: Optional[str] = None
