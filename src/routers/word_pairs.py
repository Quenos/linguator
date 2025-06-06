from fastapi import APIRouter, Body, HTTPException, status, Depends, Request, Query
from fastapi.responses import Response, JSONResponse
from fastapi.encoders import jsonable_encoder
from typing import List, Optional
from bson import ObjectId
from datetime import datetime
from pymongo import ReturnDocument # Import necessary for find_one_and_update option
from pydantic import BaseModel, Field # Add this import

# Assuming database.py and models.py are in the parent directory (src)
# Adjust imports based on your project structure if necessary
from ..database import get_database # Use relative import
from ..models import WordPairBase, WordPairInDB, PyObjectId # Use relative import

# We need access to the database collection
# Let's assume a function get_word_pair_collection exists in database.py or we define it here
from motor.motor_asyncio import AsyncIOMotorDatabase, AsyncIOMotorCollection

COLLECTION_NAME = "word_pairs"

# --- New model for updating metrics ---
class WordPairMetricUpdate(BaseModel):
    """Model for updating a word pair's metrics."""
    is_correct: bool = Field(..., description="Whether the answer was correct")
# --- End new model ---

# --- Helper Dependency for ID Validation ---
async def validate_object_id(id: str) -> ObjectId:
    """Dependency to validate the MongoDB ObjectId string from the path."""
    try:
        return ObjectId(id)
    except Exception:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid ObjectId format: {id}")
# --- End Helper Dependency ---

def get_word_pair_collection(db: AsyncIOMotorDatabase = Depends(get_database)) -> AsyncIOMotorCollection:
    """Dependency to get the word_pairs collection."""
    return db[COLLECTION_NAME]

router = APIRouter(
    # prefix="/word-pairs", # Keep prefix in main.py's include_router for flexibility
    tags=["word-pairs"], # Tag for OpenAPI documentation
    responses={404: {"description": "Not found"}}, # Default 404 response
)

# --- CRUD Endpoints ---

@router.post(
    "/",
    response_description="Add new word pair",
    response_model=WordPairInDB,
    status_code=status.HTTP_201_CREATED
)
async def create_word_pair(word_pair: WordPairBase = Body(...), collection: AsyncIOMotorCollection = Depends(get_word_pair_collection)):
    """Create a new word pair in the database."""
    word_pair_data = jsonable_encoder(word_pair)
    # Add timestamps explicitly
    now = datetime.utcnow()
    word_pair_data["created_at"] = now
    word_pair_data["updated_at"] = now

    new_word_pair = await collection.insert_one(word_pair_data)
    created_record = await collection.find_one({"_id": new_word_pair.inserted_id})

    # Convert the MongoDB document (dict) back into our Pydantic model for the response
    # Pydantic V2 uses model_validate
    return WordPairInDB.model_validate(created_record)


@router.get(
    "/",
    response_description="List all word pairs",
    response_model=List[WordPairInDB]
)
async def list_word_pairs(
    collection: AsyncIOMotorCollection = Depends(get_word_pair_collection),
    limit: Optional[int] = Query(None, description="Limit the number of word pairs returned, used for practice sessions")
):
    """Retrieve word pairs. Optionally limits the number returned."""
    query = {} # Empty query to find all
    word_pairs_cursor = collection.find(query)

    if limit is not None and limit > 0:
        word_pairs_cursor = word_pairs_cursor.limit(limit) # Apply limit if provided

    word_pairs = []
    async for pair in word_pairs_cursor:
        word_pairs.append(WordPairInDB.model_validate(pair))

    return word_pairs # Always return JSON list


@router.get(
    "/{id}",
    response_description="Get a single word pair",
    response_model=WordPairInDB
)
async def show_word_pair(obj_id: ObjectId = Depends(validate_object_id), collection: AsyncIOMotorCollection = Depends(get_word_pair_collection)):
    """Get a single word pair by its validated ID."""
    # obj_id is already validated by the dependency
    word_pair = await collection.find_one({"_id": obj_id})
    if word_pair is not None:
        return WordPairInDB.model_validate(word_pair)

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Word pair with ID {obj_id} not found")


@router.put(
    "/{id}",
    response_description="Update a word pair",
    response_model=WordPairInDB # Return the updated document
)
async def update_word_pair(
    obj_id: ObjectId = Depends(validate_object_id),
    word_pair_update: WordPairBase = Body(...),
    collection: AsyncIOMotorCollection = Depends(get_word_pair_collection)
):
    """Update an existing word pair by its validated ID using find_one_and_update."""
    update_data = word_pair_update.model_dump(exclude_unset=True) # Pydantic V2

    # Don't update if there's nothing to update, prevents unnecessary db call and timestamp bump
    if not update_data:
         # Optionally, fetch and return the existing document or raise an error/return specific status
         existing_doc = await collection.find_one({"_id": obj_id})
         if existing_doc:
             return WordPairInDB.model_validate(existing_doc)
         else:
              raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Word pair with ID {obj_id} not found")


    # Add/update the updated_at timestamp
    update_data["updated_at"] = datetime.utcnow()

    # Use find_one_and_update to perform the update and return the *new* document
    updated_doc = await collection.find_one_and_update(
        {"_id": obj_id},
        {"$set": update_data},
        return_document=ReturnDocument.AFTER # Ensure we get the document post-update
    )

    if updated_doc:
        return WordPairInDB.model_validate(updated_doc)
    else:
        # If find_one_and_update returns None, it means the document with the ID wasn't found
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Word pair with ID {obj_id} not found")


@router.delete("/{id}", response_description="Delete a word pair", status_code=status.HTTP_204_NO_CONTENT)
async def delete_word_pair(
    obj_id: ObjectId = Depends(validate_object_id),
    collection: AsyncIOMotorCollection = Depends(get_word_pair_collection)
):
    """Delete a word pair by its validated ID."""
    # obj_id is already validated by the dependency
    delete_result = await collection.delete_one({"_id": obj_id})

    if delete_result.deleted_count == 1:
        # Return No Content which is standard for DELETE success
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Word pair with ID {obj_id} not found")

# --- New endpoint for updating metrics ---
@router.post(
    "/{id}/metrics",
    response_description="Update metrics for a word pair",
    response_model=WordPairInDB
)
async def update_word_pair_metrics(
    obj_id: ObjectId = Depends(validate_object_id),
    metric_update: WordPairMetricUpdate = Body(...),
    collection: AsyncIOMotorCollection = Depends(get_word_pair_collection)
):
    """
    Update metrics for a word pair based on whether the answer was correct.
    Increments either correct_count or incorrect_count depending on is_correct field.
    """
    # Determine which field to increment based on is_correct
    field_to_increment = "correct_count" if metric_update.is_correct else "incorrect_count"
    
    # Update the document using MongoDB's $inc operator
    updated_doc = await collection.find_one_and_update(
        {"_id": obj_id},
        {
            "$inc": {field_to_increment: 1},
            "$set": {"updated_at": datetime.utcnow()}
        },
        return_document=ReturnDocument.AFTER
    )
    
    if updated_doc:
        return WordPairInDB.model_validate(updated_doc)
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Word pair with ID {obj_id} not found")
# --- End new endpoint --- 