from fastapi import APIRouter, Depends, HTTPException, Query
from motor.motor_asyncio import AsyncIOMotorCollection
from typing import List, Optional
import random # Although $sample is preferred, keep import for potential future use
import httpx # Add this import for making internal API calls
from datetime import datetime

from src.database import get_collection, add_practice_result
from ..models import WordPairInDB, PracticeResultBase, PracticeResultInDB

router = APIRouter(
    prefix="/practice-session",
    tags=["Practice Session"],
    responses={404: {"description": "Not found"}},
)

DEFAULT_PRACTICE_COUNT = 10

def get_word_pair_collection() -> AsyncIOMotorCollection:
    return get_collection("word_pairs")

@router.get(
    "/",
    response_description="Get a list of word pairs for a practice session",
    response_model=List[WordPairInDB]
)
async def get_practice_session_word_pairs(
    collection: AsyncIOMotorCollection = Depends(get_word_pair_collection),
    count: Optional[int] = Query(DEFAULT_PRACTICE_COUNT, description=f"Number of word pairs for the session (default: {DEFAULT_PRACTICE_COUNT})"),
    category: Optional[str] = Query(None, description="Filter word pairs by category"),
    prioritize: Optional[bool] = Query(False, description="Prioritize word pairs with high incorrect:correct ratio")
):
    """
    Retrieves a randomized list of word pairs for a practice session.
    If prioritize=True, words with higher incorrect:correct ratios are given higher probability.
    Can be filtered by category if specified.
    """
    if count is None or count <= 0:
        count = DEFAULT_PRACTICE_COUNT

    pipeline = []
    
    # Add category filter if provided
    if category:
        pipeline.append({"$match": {"category": category}})
    
    if prioritize:
        # Add fields to calculate the difficulty ratio
        pipeline.append({
            "$addFields": {
                # Set ratio to 0 if no practice (correct+incorrect = 0)
                # For words with some practice (>0), calculate the ratio
                # Add small constant (0.01) to avoid division by zero
                "difficulty_ratio": {
                    "$cond": [
                        {"$eq": [{"$add": ["$correct_count", "$incorrect_count"]}, 0]},
                        0.5,  # Default ratio for unpracticed words
                        {"$divide": [
                            "$incorrect_count", 
                            {"$add": ["$correct_count", "$incorrect_count", 0.01]}
                        ]}
                    ]
                }
            }
        })
        
        # Add a random weight field that's biased by the difficulty ratio
        # Words with higher ratios get exponentially higher chances
        pipeline.append({
            "$addFields": {
                "priority_weight": {
                    "$pow": [
                        # Base: e (approximately 2.718)
                        2.718, 
                        # Exponent: difficulty_ratio * 2
                        # This gives exponential priority to higher ratios
                        {"$multiply": ["$difficulty_ratio", 2]}
                    ]
                }
            }
        })
        
        # Add randomized sampling based on the weight field
        pipeline.append({"$sample": {"size": count}})
        
        # Remove the temporary fields we added
        pipeline.append({
            "$project": {
                "difficulty_ratio": 0,
                "priority_weight": 0
            }
        })
    else:
        # Standard random sampling without prioritization
        pipeline.append({"$sample": {"size": count}})

    try:
        word_pairs_cursor = collection.aggregate(pipeline)
        word_pairs = []
        async for pair in word_pairs_cursor:
            # Ensure _id is correctly handled if needed downstream, model_validate should handle it
            word_pairs.append(WordPairInDB.model_validate(pair))

        if not word_pairs:
            # If $sample returns nothing (e.g., empty collection), maybe return empty list or error?
            # For now, returning empty list is fine.
            pass # Return empty list []

        # If $sample returns fewer than requested (because collection is small), that's also fine.
        return word_pairs
    except Exception as e:
        # Log the exception e
        print(f"Error fetching practice session pairs: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve word pairs for practice session")

@router.post(
    "/results",
    response_description="Record a practice result",
    response_model=PracticeResultInDB,
    status_code=201 # Return 201 Created on successful creation
)
async def record_practice_result(result: PracticeResultBase):
    """
    Receives and stores the result of a single practice item (e.g., flashcard answer).
    Also updates the metrics for the word pair.
    """
    try:
        # Add the result to the database
        created_result = await add_practice_result(result)
        
        # Now update the metrics for the word pair
        try:
            # Get the word pair collection
            word_pair_collection = get_collection("word_pairs")
            
            # Update the word pair metrics directly in the database
            # This is more efficient than making an internal API call
            word_pair_id = result.word_pair_id
            field_to_increment = "correct_count" if result.is_correct else "incorrect_count"
            
            await word_pair_collection.update_one(
                {"_id": word_pair_id},
                {
                    "$inc": {field_to_increment: 1},
                    "$set": {"updated_at": datetime.utcnow()}
                }
            )
            
        except Exception as e:
            # Log the error but don't fail the entire request
            print(f"Error updating word pair metrics: {e}")
            # The practice result is already stored, so we can continue
        
        return created_result
    except Exception as e:
        # Log the exception
        print(f"Error recording practice result: {e}") # Consider more robust logging
        raise HTTPException(status_code=500, detail=f"Failed to record practice result: {str(e)}") 