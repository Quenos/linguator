from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
# Import the database function
from ..database import calculate_progress_stats, get_database # Assuming calculate_progress_stats is in database.py
import logging

logger = logging.getLogger(__name__)

# Define the response model for progress statistics
class ProgressStatsResponse(BaseModel):
    total_unique_words_practiced: int = Field(..., description="Total number of unique word pairs practiced")
    overall_accuracy_percentage: Optional[float] = Field(None, description="Overall accuracy percentage (correct / total attempts). Null if no attempts.")

# Create the router for progress endpoints
router = APIRouter(
    prefix="/progress",
    tags=["progress"],
    responses={404: {"description": "Not found"}},
)

# Updated endpoint to use the database function
@router.get("/stats", response_model=ProgressStatsResponse)
async def get_progress_stats():
    """Fetches and returns basic progress statistics."""
    try:
        stats = await calculate_progress_stats()
        # The function already returns the correct structure, including None for accuracy if no attempts
        # We just need to ensure the keys match the Pydantic model
        return ProgressStatsResponse(
            total_unique_words_practiced=stats.get("total_unique_words_practiced", 0),
            overall_accuracy_percentage=stats.get("overall_accuracy_percentage") # Will be None if not present or explicitly None
        )
    except Exception as e:
        logger.error(f"Failed to get progress stats: {e}")
        # Re-raise as an HTTPException to provide a proper API error response
        raise HTTPException(status_code=500, detail="Failed to calculate progress statistics") 