from fastapi import APIRouter, Body, HTTPException, status, Depends
from fastapi.responses import Response, JSONResponse
from fastapi.encoders import jsonable_encoder
from typing import List
from bson import ObjectId
from datetime import datetime

# Assuming database.py and models.py are in the parent directory (src)
# Adjust imports based on your project structure if necessary
from ..database import get_database # Use relative import
from ..models import WordPairBase, WordPairInDB, PyObjectId # Use relative import

# We need access to the database collection
# Let's assume a function get_word_pair_collection exists in database.py or we define it here
from motor.motor_asyncio import AsyncIOMotorDatabase, AsyncIOMotorCollection

COLLECTION_NAME = "word_pairs"

def get_word_pair_collection(db: AsyncIOMotorDatabase = Depends(get_database)) -> AsyncIOMotorCollection:
    """Dependency to get the word_pairs collection."""
    return db[COLLECTION_NAME]


router = APIRouter(
    prefix="/word-pairs",
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
async def list_word_pairs(collection: AsyncIOMotorCollection = Depends(get_word_pair_collection)):
    """Retrieve all word pairs from the database."""
    word_pairs = []
    async for pair in collection.find():
        word_pairs.append(WordPairInDB.model_validate(pair))
    return word_pairs


@router.get(
    "/{id}",
    response_description="Get a single word pair",
    response_model=WordPairInDB
)
async def show_word_pair(id: str, collection: AsyncIOMotorCollection = Depends(get_word_pair_collection)):
    """Get a single word pair by its ID."""
    try:
        obj_id = ObjectId(id)
    except Exception:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid ObjectId format: {id}")

    word_pair = await collection.find_one({"_id": obj_id})
    if word_pair is not None:
        return WordPairInDB.model_validate(word_pair)

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Word pair with ID {id} not found")


@router.put(
    "/{id}",
    response_description="Update a word pair",
    response_model=WordPairInDB # Return the updated document
)
async def update_word_pair(id: str, word_pair_update: WordPairBase = Body(...), collection: AsyncIOMotorCollection = Depends(get_word_pair_collection)):
    """Update an existing word pair by its ID."""
    try:
        obj_id = ObjectId(id)
    except Exception:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid ObjectId format: {id}")

    # Prepare update data, exclude unset fields if you only want partial updates
    update_data = word_pair_update.model_dump(exclude_unset=True) # Pydantic V2

    # Add/update the updated_at timestamp
    update_data["updated_at"] = datetime.utcnow()

    if len(update_data) >= 1:
        update_result = await collection.update_one(
            {"_id": obj_id},
            {"$set": update_data}
        )

        if update_result.modified_count == 1:
            # Fetch the updated document to return it
            updated_doc = await collection.find_one({"_id": obj_id})
            if updated_doc:
                 return WordPairInDB.model_validate(updated_doc)

    # Check if the document existed at all before attempting update
    existing_doc = await collection.find_one({"_id": obj_id})
    if existing_doc is not None:
        # Document exists but wasn't modified (e.g., update data was the same)
        # Return the existing document
        return WordPairInDB.model_validate(existing_doc)

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Word pair with ID {id} not found")


@router.delete("/{id}", response_description="Delete a word pair", status_code=status.HTTP_204_NO_CONTENT)
async def delete_word_pair(id: str, collection: AsyncIOMotorCollection = Depends(get_word_pair_collection)):
    """Delete a word pair by its ID."""
    try:
        obj_id = ObjectId(id)
    except Exception:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid ObjectId format: {id}")

    delete_result = await collection.delete_one({"_id": obj_id})

    if delete_result.deleted_count == 1:
        # Return No Content which is standard for DELETE success
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Word pair with ID {id} not found") 