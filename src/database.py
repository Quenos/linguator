import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

load_dotenv()  # Load environment variables from .env file

class DatabaseManager:
    """Manages MongoDB connection and provides access to the database."""
    _client: AsyncIOMotorClient | None = None
    _db = None

    def __init__(self):
        """Initializes the DatabaseManager with connection details from environment variables."""
        # Read individual components from environment variables
        mongo_user = os.getenv("MONGO_USER")
        mongo_passwd = os.getenv("MONGO_PASSWD")
        mongo_ip = os.getenv("MONGO_IP", "localhost") # Default to localhost
        mongo_port = os.getenv("MONGO_PORT", "27017") # Default MongoDB port
        self._mongo_db_name = os.getenv("MONGO_DB_NAME", "linguator") # Default DB name

        # Construct the MongoDB URI
        if mongo_user and mongo_passwd:
            # Note: Passwords should be URL-encoded if they contain special characters.
            # motor/pymongo handles basic encoding, but complex passwords might need explicit encoding.
            # Consider using urllib.parse.quote_plus if issues arise.
            self._mongodb_uri = f"mongodb://{mongo_user}:{mongo_passwd}@{mongo_ip}:{mongo_port}"
        else:
            # Connect without authentication if user/password are not provided
            self._mongodb_uri = f"mongodb://{mongo_ip}:{mongo_port}/{self._mongo_db_name}"
            logger.warning(f"MONGO_USER or MONGO_PASSWD not found in .env. Connecting without authentication to mongodb://{mongo_ip}:{mongo_port}/{self._mongo_db_name}")

        # Log the URI without credentials for security
        logger.info(f"Database URI configured for: mongodb://{mongo_ip}:{mongo_port}/{self._mongo_db_name}")


    async def connect_to_mongo(self):
        """Establishes the connection to the MongoDB server."""
        if self._client:
            logger.info("MongoDB connection already established.")
            return

        logger.info(f"Attempting to connect to MongoDB...")
        try:
            # Set a reasonable timeout for server selection
            self._client = AsyncIOMotorClient(self._mongodb_uri, serverSelectionTimeoutMS=5000)
            # Assign the database object
            self._db = self._client[self._mongo_db_name]
            # Verify connection by pinging the admin database
            await self._client.admin.command('ping')
            logger.info(f"Successfully connected to MongoDB database: {self._db.name}")
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            self._client = None
            self._db = None
            # Propagate the error to signal connection failure
            raise RuntimeError(f"Could not connect to MongoDB: {e}")

    async def close_mongo_connection(self):
        """Closes the MongoDB connection if it's currently open."""
        if self._client:
            logger.info("Closing MongoDB connection...")
            self._client.close()
            self._client = None
            self._db = None
            logger.info("MongoDB connection closed.")
        else:
            logger.info("MongoDB connection already closed or never established.")

    def get_database(self):
        """
        Returns the database instance.

        Raises:
            RuntimeError: If the database has not been initialized (i.e., connect_to_mongo was not called or failed).
        """
        if self._db is None:
            logger.error("Database access attempted before successful connection.")
            raise RuntimeError("Database not initialized. Call connect_to_mongo first and ensure it succeeds.")
        return self._db

    def get_collection(self, collection_name: str):
        """
        Returns a collection instance from the initialized database.

        Args:
            collection_name: The name of the collection to retrieve.

        Returns:
            An AsyncIOMotorCollection instance.

        Raises:
            RuntimeError: If the database has not been initialized.
        """
        return self.get_database().get_collection(collection_name)

# Instantiate the manager - Provides a single point of control for DB access
db_manager = DatabaseManager()

# Expose the necessary functions for application lifecycle management and data access
connect_to_mongo = db_manager.connect_to_mongo
close_mongo_connection = db_manager.close_mongo_connection
get_database = db_manager.get_database
get_collection = db_manager.get_collection

# Example of how to get a specific collection (can be used in other modules)
# from .database import get_collection
#
# async def some_function():
#     word_pair_collection = get_collection("word_pairs")
#     # Now you can use word_pair_collection for database operations
#     # e.g., await word_pair_collection.insert_one({"key": "value"})

# Example of how to get a collection
# def get_word_pair_collection():
#    database = get_database()
#    return database.get_collection("word_pairs") 