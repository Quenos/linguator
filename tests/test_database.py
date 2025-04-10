import pytest
import pytest_asyncio # Import pytest_asyncio
from src.database import connect_to_mongo, close_mongo_connection, get_database

@pytest.mark.asyncio
async def test_mongo_connection():
    """Tests if the application can connect to MongoDB."""
    try:
        await connect_to_mongo()
        # Verify that the database object is accessible after connection
        db = get_database()
        assert db is not None
        assert db.name == "linguator" # Check if connected to the correct DB
        # Optional: Ping the server again within the test if desired
        # await db.command('ping') 
        print("\nSuccessfully connected to MongoDB for testing.")
    except Exception as e:
        pytest.fail(f"Failed to connect to MongoDB: {e}")
    finally:
        # Ensure connection is closed regardless of test outcome
        await close_mongo_connection()
        print("MongoDB connection closed after test.")

# Example of how you might structure future tests for collections (not run yet)
# @pytest.mark.asyncio
# async def test_word_pair_collection_access():
#     """Tests if the word_pairs collection can be accessed."""
#     try:
#         await connect_to_mongo()
#         db = get_database()
#         # Try getting the collection (replace with your actual function later)
#         # collection = get_word_pair_collection() 
#         collection = db.get_collection("word_pairs") # Directly access for now
#         assert collection is not None
#         assert collection.name == "word_pairs"
#     except Exception as e:
#         pytest.fail(f"Failed to access word_pairs collection: {e}")
#     finally:
#         await close_mongo_connection()

# Fixture to manage connection for multiple tests (alternative approach)
# @pytest_asyncio.fixture(scope="module", autouse=True) # Use pytest_asyncio.fixture
# async def manage_mongo_connection():
#     """Connects before tests and closes after."""
#     try:
#         await connect_to_mongo()
#         yield # Tests run here
#     finally:
#         await close_mongo_connection()

# @pytest.mark.asyncio
# async def test_mongo_connection_with_fixture():
#     """Tests connection using the fixture."""
#     db = get_database()
#     assert db is not None
#     assert db.name == "linguator"
#     print("\nSuccessfully verified MongoDB connection via fixture.") 