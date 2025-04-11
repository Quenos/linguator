import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from httpx import AsyncClient, ASGITransport # Use AsyncClient and ASGITransport for async tests
from bson import ObjectId
from datetime import datetime, timedelta

# Import necessary components from your application
from src.main import app # Assuming your FastAPI app instance is named 'app' in src/main.py
from src.database import connect_to_mongo, close_mongo_connection, get_collection
from src.models import PracticeResultInDB, WordPairInDB, WordPairBase

# Use AsyncClient for async app
# Remove the potentially conflicting event_loop fixture
# @pytest_asyncio.fixture(scope="session")
# def event_loop():
#     """Overrides pytest default function scoped event loop"""
#     import asyncio
#     loop = asyncio.get_event_loop_policy().new_event_loop()
#     yield loop
#     loop.close()

@pytest_asyncio.fixture(scope="function", autouse=True)
async def db_connection():
    """Connects to the database before tests and closes after."""
    print("\nSetting up database connection for test function...")
    await connect_to_mongo()
    # Optional: Add logic here to clear relevant test collections if needed
    # E.g., await get_collection("word_pairs").delete_many({})
    # E.g., await get_collection("practice_results").delete_many({})
    yield
    print("\nTearing down database connection after test function...")
    await close_mongo_connection()

@pytest_asyncio.fixture(scope="function")
async def client() -> AsyncClient:
     """Provides an async test client for making requests to the app."""
     # Use ASGITransport for httpx with FastAPI async app
     async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client


@pytest_asyncio.fixture(scope="function")
async def test_word_pair() -> WordPairInDB:
    """Creates a test word pair and cleans it up afterwards."""
    collection = get_collection("word_pairs")
    now = datetime.utcnow()
    word_pair_data = WordPairBase(
        source_word="test_src",
        target_word="test_tgt",
        category="test"
    )
    word_pair_dict = word_pair_data.model_dump()
    word_pair_dict["created_at"] = now
    word_pair_dict["updated_at"] = now

    insert_result = await collection.insert_one(word_pair_dict)
    created_doc = await collection.find_one({"_id": insert_result.inserted_id})
    
    if not created_doc:
        pytest.fail("Failed to create test word pair in fixture")

    # Use WordPairInDB for validation before returning
    word_pair_obj = WordPairInDB.model_validate(created_doc) 
    print(f"\nCreated test word pair: {word_pair_obj.id}")

    yield word_pair_obj # Provide the created word pair object (including ID)

    # Cleanup
    delete_result = await collection.delete_one({"_id": word_pair_obj.id})
    print(f"\nCleaned up test word pair: {word_pair_obj.id} (Deleted: {delete_result.deleted_count})")


@pytest.mark.asyncio
async def test_record_practice_result_success(client: AsyncClient, test_word_pair: WordPairInDB):
    """Tests successfully recording a practice result."""
    practice_results_collection = get_collection("practice_results")
    payload = {
        "word_pair_id": str(test_word_pair.id),
        "is_correct": True
    }

    response = await client.post("/practice-session/results", json=payload)

    assert response.status_code == 201
    response_data = response.json()

    # Validate response structure and data
    assert "_id" in response_data
    assert response_data["word_pair_id"] == payload["word_pair_id"]
    assert response_data["is_correct"] == payload["is_correct"]
    assert "timestamp" in response_data

    # Verify timestamp is recent (e.g., within the last 5 seconds)
    timestamp = datetime.fromisoformat(response_data["timestamp"].replace('Z', '+00:00'))
    assert datetime.utcnow().replace(tzinfo=None) - timestamp.replace(tzinfo=None) < timedelta(seconds=5)

    # Verify data was saved in the database
    saved_result = await practice_results_collection.find_one({"_id": ObjectId(response_data["_id"])})
    assert saved_result is not None
    assert str(saved_result["word_pair_id"]) == payload["word_pair_id"]
    assert saved_result["is_correct"] == payload["is_correct"]
    assert saved_result["timestamp"] is not None

    # Cleanup the created practice result
    await practice_results_collection.delete_one({"_id": ObjectId(response_data["_id"])})
    print(f"\nCleaned up practice result: {response_data['_id']}")

@pytest.mark.asyncio
@pytest.mark.parametrize("invalid_payload, expected_detail_part", [
    ({"is_correct": True}, "word_pair_id"), # Missing word_pair_id
    ({"word_pair_id": str(ObjectId())}, "is_correct"), # Missing is_correct
    ({"word_pair_id": "not-an-objectid", "is_correct": False}, "word_pair_id"), # Invalid word_pair_id format
    ({}, "word_pair_id"), # Empty payload
])
async def test_record_practice_result_invalid_payload(client: AsyncClient, invalid_payload: dict, expected_detail_part: str):
    """Tests recording a practice result with invalid payloads."""
    response = await client.post("/practice-session/results", json=invalid_payload)

    assert response.status_code == 422 # Unprocessable Entity
    response_data = response.json()
    assert "detail" in response_data
    # Check if the expected field name is mentioned in the validation error detail
    assert any(expected_detail_part in error.get("loc", []) for error in response_data["detail"]) 