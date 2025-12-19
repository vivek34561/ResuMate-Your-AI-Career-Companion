"""
User Settings API routes
"""

from fastapi import APIRouter, HTTPException, Depends, status
from typing import Optional

from api.models import (
    UserSettings,
    UserSettingsUpdate,
    SuccessResponse,
)
from api.routes.auth import verify_token
from database import get_user_settings, save_user_settings

router = APIRouter()


@router.get("/", response_model=UserSettings)
async def get_settings(user: dict = Depends(verify_token)):
    """
    Get user settings
    
    Requires: Bearer token in Authorization header
    """
    """
    Deprecated: FastAPI backend removed. This module is no longer used.
    """

    raise RuntimeError("FastAPI routes removed. Use Streamlit-only frontend.")
            )
        
        return UserSettings(
            provider=settings.get("provider", "groq"),
            api_key=settings.get("api_key"),
            model=settings.get("model"),
            ollama_base_url=settings.get("ollama_base_url", "http://localhost:11434"),
            ollama_model=settings.get("ollama_model", "llama3.1:8b")
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch settings: {str(e)}"
        )


@router.put("/", response_model=SuccessResponse)
async def update_settings(
    settings: UserSettingsUpdate,
    user: dict = Depends(verify_token)
):
    """
    Update user settings
    
    - **provider**: LLM provider (openai, groq, ollama)
    - **api_key**: API key for the provider
    - **model**: Model name
    - **ollama_base_url**: Ollama base URL (for ollama provider)
    - **ollama_model**: Ollama model name (for ollama provider)
    
    Requires: Bearer token in Authorization header
    """
    try:
        user_id = user["user_id"]
        
        # Get current settings
        current_settings = get_user_settings(user_id) or {}
        
        # Update with new values (only if provided)
        if settings.provider is not None:
            current_settings["provider"] = settings.provider.value
        
        if settings.api_key is not None:
            current_settings["api_key"] = settings.api_key
        
        if settings.model is not None:
            current_settings["model"] = settings.model
        
        if settings.ollama_base_url is not None:
            current_settings["ollama_base_url"] = settings.ollama_base_url
        
        if settings.ollama_model is not None:
            current_settings["ollama_model"] = settings.ollama_model
        
        # Save updated settings
        success = save_user_settings(user_id, current_settings)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to save settings"
            )
        
        return SuccessResponse(
            success=True,
            message="Settings updated successfully"
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update settings: {str(e)}"
        )


@router.delete("/")
async def reset_settings(user: dict = Depends(verify_token)):
    """
    Reset user settings to defaults
    
    Requires: Bearer token in Authorization header
    """
    try:
        user_id = user["user_id"]
        
        # Reset to default settings
        default_settings = {
            "provider": "groq",
            "api_key": None,
            "model": None,
            "ollama_base_url": "http://localhost:11434",
            "ollama_model": "llama3.1:8b"
        }
        
        success = save_user_settings(user_id, default_settings)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to reset settings"
            )
        
        return SuccessResponse(
            success=True,
            message="Settings reset to defaults"
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to reset settings: {str(e)}"
        )
