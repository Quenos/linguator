# scripts/seed_db.py
import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

load_dotenv()  # Load environment variables from .env file

# Sample data to insert
SAMPLE_DATA = [
    {"source_word": "hello", "target_word": "hallo", "category": "greeting", "example_sentence": "Say hello!"},
    {"source_word": "world", "target_word": "Welt", "category": "noun", "example_sentence": "Hello world!"},
    {"source_word": "thank you", "target_word": "danke", "category": "phrase", "example_sentence": "Thank you very much."},
    {"source_word": "computer", "target_word": "Computer", "category": "technology", "example_sentence": "The computer is fast."},
    {"source_word": "language", "target_word": "Sprache", "category": "general", "example_sentence": "Learning a new language."}
]

async def seed_database():
    """Connects to the database and inserts sample word pairs if they don't exist."""
    client = None  # Initialize client to None
    try:
        # Read connection details from environment variables
        mongo_user = os.getenv("MONGO_USER")
        mongo_passwd = os.getenv("MONGO_PASSWD")
        mongo_ip = os.getenv("MONGO_IP", "localhost")
        mongo_port = os.getenv("MONGO_PORT", "27017")
        mongo_db_name = os.getenv("MONGO_DB_NAME", "linguator")
        collection_name = "word_pairs"

        # Construct URI
        if mongo_user and mongo_passwd:
            mongodb_uri = f"mongodb://{mongo_user}:{mongo_passwd}@{mongo_ip}:{mongo_port}"
        else:
            mongodb_uri = f"mongodb://{mongo_ip}:{mongo_port}/"
            logger.warning(f"MONGO_USER or MONGO_PASSWD not found. Connecting without authentication to {mongodb_uri}")

        logger.info(f"Connecting to MongoDB at {mongo_ip}:{mongo_port}...")
        client = AsyncIOMotorClient(mongodb_uri, serverSelectionTimeoutMS=5000)
        db = client[mongo_db_name]
        collection = db[collection_name]

        # Check if data already exists (simple check based on one item)
        existing_check = await collection.find_one({"source_word": SAMPLE_DATA[0]["source_word"]})
        if existing_check:
            logger.info(f"Sample data already exists in '{collection_name}'. Skipping insertion.")
            return

        logger.info(f"Inserting sample data into '{collection_name}' collection...")
        now = datetime.utcnow()
        data_to_insert = []
        for item in SAMPLE_DATA:
            item['created_at'] = now
            item['updated_at'] = now
            data_to_insert.append(item)

        result = await collection.insert_many(data_to_insert)
        logger.info(f"Successfully inserted {len(result.inserted_ids)} sample word pairs.")

    except Exception as e:
        logger.error(f"An error occurred during database seeding: {e}")
    finally:
        if client:
            client.close()
            logger.info("MongoDB connection closed.")

if __name__ == "__main__":
    asyncio.run(seed_database()) 