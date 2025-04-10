import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import urllib.parse # Import urllib.parse

load_dotenv()  # Load environment variables from .env file

# Read individual components from environment variables
MONGO_USER = os.getenv("MONGO_USER")
MONGO_PASSWD = os.getenv("MONGO_PASSWD")
MONGO_IP = os.getenv("MONGO_IP", "localhost") # Default to localhost
MONGO_PORT = os.getenv("MONGO_PORT", "27017")   # Default MongoDB port
MONGO_DB_NAME = "linguator" 

# Construct the MongoDB URI
if MONGO_USER and MONGO_PASSWD:
    MONGODB_URI = f"mongodb://{MONGO_USER}:{MONGO_PASSWD}@{MONGO_IP}:{MONGO_PORT}"
else:
    # Connect without authentication if user/password are not provided
    MONGODB_URI = f"mongodb://{MONGO_IP}:{MONGO_PORT}/{MONGO_DB_NAME}"
    print(f"Warning: MONGO_USER or MONGO_PASSWD not found in .env. Connecting without authentication to {MONGO_IP}:{MONGO_PORT}.")


print(f"Database URI configured: {MONGODB_URI}") # Log the URI being used (optional)

client: AsyncIOMotorClient | None = None
db = MONGO_DB_NAME

async def connect_to_mongo():
    """Connects to MongoDB and initializes the client and db variables."""
    global client, db
    print(f"Connecting to MongoDB at {MONGODB_URI}...")
    try:
        client = AsyncIOMotorClient(MONGODB_URI)
        # The database name is already part of the URI
        db = client[MONGO_DB_NAME] # Get the database object from the client
        # Optional: Ping the server to verify connection
        await client.admin.command('ping')
        print(f"Connected to MongoDB database: {db.name}")
    except Exception as e:
        print(f"Error connecting to MongoDB: {e}")
        # Depending on your error handling strategy, you might want to:
        # - Set client/db back to None
        # - Raise the exception to stop the application startup
        client = None
        db = None
        raise RuntimeError(f"Could not connect to MongoDB: {e}")


async def close_mongo_connection():
    """Closes the MongoDB connection."""
    global client
    if client:
        print("Closing MongoDB connection...")
        client.close()
        client = None
        print("MongoDB connection closed.")

def get_database():
    """Returns the database instance. Ensures connect_to_mongo is called first."""
    if db is None:
        raise RuntimeError("Database not initialized. Call connect_to_mongo first.")
    return db

# Example of how to get a collection
# def get_word_pair_collection():
#    database = get_database()
#    return database.get_collection("word_pairs") 