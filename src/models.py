from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Any
from datetime import datetime
from bson import ObjectId # Import ObjectId
from pydantic_core import core_schema # Import core_schema
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
        def validate_from_input(value: Any) -> ObjectId:
            if isinstance(value, ObjectId):
                return value
            if ObjectId.is_valid(str(value)): # Try converting to string first
                return ObjectId(str(value))
            raise ValueError(f"Invalid ObjectId: {value}")

        # Schema for input: Accepts str or ObjectId
        # Use core_schema.with_info_plain_validator_function for compatibility
        # with potential future context needs, though not used here.
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
        arbitrary_types_allowed = True, # Still needed for ObjectId if not using __get_pydantic_core_schema__ fully
        json_encoders = {ObjectId: str}, # Still useful for custom encoding if needed
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
# class WordPairUpdate(BaseModel):
#    source_word: Optional[str]
#    target_word: Optional[str]
#    category: Optional[str]
#    example_sentence: Optional[str]
#    updated_at: datetime = Field(default_factory=datetime.utcnow) # Force update timestamp 