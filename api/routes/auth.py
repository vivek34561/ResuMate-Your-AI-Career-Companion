"""
Authentication API routes
"""

from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
import jwt
import os
from datetime import datetime, timedelta

from api.models import (
    UserRegister,
    UserLogin,
    Token,
    SuccessResponse,
    ErrorResponse
)
from database import (
    create_user,
    authenticate_user,
    get_user_by_email,
)

router = APIRouter()
security = HTTPBearer()

# JWT Configuration
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 days


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify JWT token and return user data"""
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("user_id")
        email: str = payload.get("email")
        
        if user_id is None or email is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials"
            )
        
        return {"user_id": user_id, "email": email}
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired"
        )
    except jwt.JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )


@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
async def register_user(user: UserRegister):
    """
    Register a new user
    
    - **email**: Valid email address
    - **password**: Password (min 8 characters)
    - **full_name**: Optional full name
    """
    try:
        # Check if user already exists
        existing_user = get_user_by_email(user.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Create new user
        user_id = create_user(user.email, user.password)
        
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create user"
            )
        
        # Create access token
        access_token = create_access_token(
            data={"user_id": user_id, "email": user.email}
        )
        
        return Token(
            access_token=access_token,
            token_type="bearer",
            user_id=user_id,
            email=user.email
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}"
        )


@router.post("/login", response_model=Token)
async def login_user(credentials: UserLogin):
    """
    Login with email and password
    
    - **email**: User's email
    - **password**: User's password
    """
    try:
        user = authenticate_user(credentials.email, credentials.password)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        # Create access token
        access_token = create_access_token(
            data={"user_id": user["id"], "email": user["email"]}
        )
        
        return Token(
            access_token=access_token,
            token_type="bearer",
            user_id=user["id"],
            email=user["email"]
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Login failed: {str(e)}"
        )


 


@router.get("/me")
async def get_current_user(user: dict = Depends(verify_token)):
    """
    Get current user information
    
    Requires: Bearer token in Authorization header
    """
    return {
        "user_id": user["user_id"],
        "email": user["email"]
    }


@router.post("/logout")
async def logout_user(user: dict = Depends(verify_token)):
    """
    Logout current user (client should discard token)
    
    Requires: Bearer token in Authorization header
    """
    return SuccessResponse(
        success=True,
        message="Logged out successfully"
    )


@router.post("/refresh", response_model=Token)
async def refresh_token(user: dict = Depends(verify_token)):
    """
    Refresh access token
    
    Requires: Bearer token in Authorization header
    """
    try:
        # Create new access token
        access_token = create_access_token(
            data={"user_id": user["user_id"], "email": user["email"]}
        )
        
        return Token(
            access_token=access_token,
            token_type="bearer",
            user_id=user["user_id"],
            email=user["email"]
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Token refresh failed: {str(e)}"
        )
