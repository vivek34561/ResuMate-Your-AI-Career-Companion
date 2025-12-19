"""
Job Search API routes
"""

from fastapi import APIRouter, HTTPException, Depends, status, Query
from typing import Optional

from api.models import (
    JobSearchRequest,
    JobSearchResponse,
    JobListing,
)
from api.routes.auth import verify_token
from agents.job_search_agent import JobAgent

router = APIRouter()


@router.post("/search", response_model=JobSearchResponse)
async def search_jobs(
    request: JobSearchRequest,
    platform: str = Query(default="adzuna", description="Job platform: adzuna | jooble"),
    user: dict = Depends(verify_token),
):
    """
    Search jobs via supported platforms.

    - Body: { query, location, max_results }
    - Query param: platform=adzuna|jooble
    """
    """
    Deprecated: FastAPI backend removed. This module is no longer used.
    """

    raise RuntimeError("FastAPI routes removed. Use Streamlit-only frontend.")
        for j in jobs or []:
            if "error" in j:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=j["error"])
            listings.append(
                JobListing(
                    title=j.get("title") or "",
                    company=j.get("company") or "",
                    location=j.get("location") or "",
                    description=j.get("description") or "",
                    url=j.get("link") or j.get("url"),
                )
            )

        return JobSearchResponse(jobs=listings, total_found=len(listings))

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Job search failed: {str(e)}",
        )
