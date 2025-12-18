"""
Utility functions for API routes
"""

import os
from functools import lru_cache
from agents import ResumeAnalysisAgent


@lru_cache(maxsize=128)
def create_agent_for_user(
    user_id: int,
    provider: str,
    api_key: str,
    model: str = None,
    ollama_base_url: str = "http://localhost:11434"
) -> ResumeAnalysisAgent:
    """
    Create and cache ResumeAnalysisAgent for a user
    
    Args:
        user_id: User ID
        provider: LLM provider (openai, groq, ollama)
        api_key: API key for the provider
        model: Optional model name
        ollama_base_url: Ollama base URL
        
    Returns:
        ResumeAnalysisAgent instance
    """
    return ResumeAnalysisAgent(
        api_key=api_key,
        provider=provider,
        model=model,
        ollama_base_url=ollama_base_url,
        user_id=user_id
    )


def clear_agent_cache():
    """Clear the agent cache"""
    create_agent_for_user.cache_clear()
