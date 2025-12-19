"""
Deprecated: FastAPI backend removed. This module is no longer used.
"""

raise RuntimeError("FastAPI routes removed. Use Streamlit-only frontend.")
        
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
