from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Any
from datetime import datetime
from bson import ObjectId # Import ObjectId
from pydantic_core import core_schema # Import core_schema
from pydantic import ValidationInfo # Import ValidationInfo from pydantic
from pydantic.json_schema import JsonSchemaValue, GetJsonSchemaHandler
from pydantic import GetCoreSchemaHandler

# Helper class for handling MongoDB ObjectId
# Updated for Pydantic V2 - Simplified
class PyObjectId(ObjectId):
    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type: Any, handler: GetCoreSchemaHandler
    ) -> core_schema.CoreSchema:
        """Define the Pydantic V2 core schema for ObjectId validation and serialization."""
        # Validator function: takes input and returns ObjectId or raises ValueError
        # Updated signature to accept optional ValidationInfo
        def validate_from_input(value: Any, info: ValidationInfo) -> ObjectId:
            # info is not used here, but the signature needs to accept it
            if isinstance(value, ObjectId):
                return value
            if ObjectId.is_valid(str(value)): # Try converting to string first
                return ObjectId(str(value))
            raise ValueError(f"Invalid ObjectId: {value}")

        # Schema for input: Accepts str or ObjectId
        # Use core_schema.with_info_plain_validator_function for compatibility
        # with potential future context needs, though not used here.
        # This validator expects a function with signature (value: Any, info: ValidationInfo)
        input_schema = core_schema.with_info_plain_validator_function(validate_from_input)

        return core_schema.json_or_python_schema(
            # Schema used for JSON parsing (expects string)
            json_schema=core_schema.chain_schema([
                core_schema.str_schema(), # Input must be a string in JSON
                input_schema
            ]),
            # Schema used for Python object validation (accepts str or ObjectId)
            python_schema=core_schema.union_schema([
                core_schema.is_instance_schema(ObjectId), # Allow ObjectId directly
                input_schema # Allow other types handled by validator
            ]),
            # How to serialize the ObjectId to JSON (as string)
            serialization=core_schema.plain_serializer_function_ser_schema(lambda x: str(x))
        )

    # Keep __get_pydantic_json_schema__ for OpenAPI documentation generation
    @classmethod
    def __get_pydantic_json_schema__(
        cls, _core_schema: core_schema.CoreSchema, handler: GetJsonSchemaHandler
    ) -> JsonSchemaValue:
        # Tell FastAPI/OpenAPI that this field is a string
        return handler(core_schema.str_schema())


class WordPairBase(BaseModel):
    """Base model for word pair data (used for creation/updates)"""
    source_word: str = Field(..., min_length=1)
    target_word: str = Field(..., min_length=1)
    category: Optional[str] = None # e.g., noun, verb, phrase
    example_sentence: Optional[str] = None

    # Pydantic V2 uses model_config instead of Config class
    model_config = ConfigDict(
        json_schema_extra = { # Renamed from schema_extra
            "example": {
                "source_word": "hello",
                "target_word": "ciao",
                "category": "greeting",
                "example_sentence": "Say hello when you see him."
            }
        }
    )

class WordPairInDB(WordPairBase):
    """Model representing a word pair as stored in the database (includes ID)"""
    id: PyObjectId = Field(..., alias="_id") # Removed default_factory, id is required
    # Timestamps are set during database operations, no default factory needed here
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        populate_by_name = True, # Renamed from allow_population_by_field_name
        json_schema_extra = { # Renamed from schema_extra
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
    )

# Optional: Model for update operations if you need different fields/validation
class WordPairUpdate(BaseModel):
   """Model for updating a word pair (all fields optional)"""
   source_word: Optional[str] = None
   target_word: Optional[str] = None
   category: Optional[str] = None
   example_sentence: Optional[str] = None
   # updated_at is typically handled by the database logic during the update operation

   model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "source_word": "goodbye",
                "target_word": "arrivederci",
                "category": "farewell"
            }
        }
    )

# Models for Practice Results
class PracticeResultBase(BaseModel):
    """Base model for recording a practice result."""
    word_pair_id: PyObjectId = Field(..., description="The ID of the WordPair practiced")
    is_correct: bool = Field(..., description="Whether the user answered correctly")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "word_pair_id": "60d5ec49f7eade7f5c9f2f5e", # Example ObjectId
                "is_correct": True,
            }
        }
    )

class PracticeResultInDB(PracticeResultBase):
    """Model representing a practice result as stored in the database."""
    id: PyObjectId = Field(..., alias="_id")
    timestamp: datetime = Field(..., description="Timestamp when the result was recorded")

    model_config = ConfigDict(
        populate_by_name=True,
        json_schema_extra={
            "example": {
                "_id": "61e0f8a7a7d8f9b3c8e4f5b1", # Example ObjectId
                "word_pair_id": "60d5ec49f7eade7f5c9f2f5e",
                "is_correct": False,
                "timestamp": "2023-01-15T10:30:00Z",
            }
        }
    ) 