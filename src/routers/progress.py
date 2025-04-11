from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
# Import the database function
from ..database import calculate_progress_stats, reset_progress_data, get_database # Added reset_progress_data import
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

# Define the response model for the reset operation
class ResetProgressResponse(BaseModel):
    deleted_count: int = Field(..., description="Number of deleted practice records")
    status: str = Field(..., description="Status of the operation")
    message: str = Field(..., description="Detailed message about the operation")

@router.delete("/reset", response_model=ResetProgressResponse)
async def reset_progress():
    """Resets all progress data by deleting all practice results."""
    try:
        result = await reset_progress_data()
        return ResetProgressResponse(**result)
    except Exception as e:
        logger.error(f"Failed to reset progress data: {e}")
        raise HTTPException(status_code=500, detail="Failed to reset progress data") 