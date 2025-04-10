from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from bson import ObjectId # Import ObjectId
from pydantic_core import core_schema # Import core_schema
from pydantic.json_schema import JsonSchemaValue, GetJsonSchemaHandler # Add this import

# Helper class for handling MongoDB ObjectId
# See: https://www.mongodb.com/developer/languages/python/python-quickstart-fastapi/
class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)

    @classmethod
    def __get_pydantic_json_schema__(
        cls,
        core_schema: core_schema.CoreSchema,
        handler: 'GetJsonSchemaHandler',
    ) -> JsonSchemaValue:
        return core_schema.str_schema()


class WordPairBase(BaseModel):
    """Base model for word pair data (used for creation/updates)"""
    source_word: str = Field(..., min_length=1)
    target_word: str = Field(..., min_length=1)
    category: Optional[str] = None # e.g., noun, verb, phrase
    example_sentence: Optional[str] = None

    class Config:
        # Example data for documentation
        schema_extra = {
            "example": {
                "source_word": "hello",
                "target_word": "ciao",
                "category": "greeting",
                "example_sentence": "Say hello when you see him."
            }
        }

class WordPairInDB(WordPairBase):
    """Model representing a word pair as stored in the database (includes ID)"""
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    # Timestamps can be added here if you want them automatically handled by Pydantic
    # Or managed during database operations
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        allow_population_by_field_name = True # Allows using '_id' when creating instance
        arbitrary_types_allowed = True # Needed for ObjectId
        json_encoders = {ObjectId: str} # Serialize ObjectId to string
        schema_extra = {
            "example": {
                "_id": "60d5ec49f7eade7f5c9f2f5e", # Example ObjectId
                "source_word": "world",
                "target_word": "mondo",
                "category": "noun",
                "example_sentence": "The world is round.",
                "created_at": "2023-01-01T12:00:00Z",
                "updated_at": "2023-01-01T12:00:00Z"
            }
        }

# Optional: Model for update operations if you need different fields/validation
# class WordPairUpdate(BaseModel):
#    source_word: Optional[str]
#    target_word: Optional[str]
#    category: Optional[str]
#    example_sentence: Optional[str]
#    updated_at: datetime = Field(default_factory=datetime.utcnow) # Force update timestamp 