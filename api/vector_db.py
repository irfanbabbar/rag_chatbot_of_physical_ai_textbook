# # vector_db.py
# import os
# from dotenv import load_dotenv
# from qdrant_client import QdrantClient
# from qdrant_client.models import VectorParams, Distance

# # Load .env
# load_dotenv()

# QDRANT_URL = os.getenv("QDRANT_URL")
# QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")

# client = QdrantClient(
#     url=QDRANT_URL,
#     api_key=QDRANT_API_KEY,
# )

# def check_collection_status():
#     print("Testing Qdrant connection...")

#     collections = client.get_collections().collections
#     names = [c.name for c in collections]

#     if os.getenv("COLLECTION_NAME") in names:
#         print(f"Collection '{os.getenv('COLLECTION_NAME')}' already exists")
#     else:
#         print("Collection does not exist")

# if __name__ == "__main__":
#     print("Testing Qdrant connection...")
#     check_collection_status()

# backend/vector_db.py

import os
from dotenv import load_dotenv
from qdrant_client import QdrantClient

# Load environment variables from the .env file
load_dotenv()

# --- Configuration ---
# Read secure keys from environment variables
QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
# Define the name of the collection where data will be stored
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "book_knowledge")

def get_qdrant_client() -> QdrantClient:
    """Initializes and returns the Qdrant client securely."""
    # Basic error checking to ensure keys are loaded
    if not QDRANT_URL or not QDRANT_API_KEY:
        raise ValueError(
            "Error: QDRANT_URL or QDRANT_API_KEY is not set in environment variables. "
            "Please configure them in Vercel dashboard or .env file."
        )

    # Create the connection to Qdrant Cloud
    try:
        client = QdrantClient(
            url=QDRANT_URL,
            api_key=QDRANT_API_KEY,
        )
        # Only print in local development
        if os.getenv("VERCEL_ENV") is None:
            print(f"Successfully connected to Qdrant at: {QDRANT_URL}")
        return client
    except Exception as e:
        raise ConnectionError(f"Failed to connect to Qdrant: {str(e)}")

# Small test to ensure it works when run directly
if __name__ == "__main__":
    try:
        client = get_qdrant_client()
        collections = client.get_collections()
        print(f"Connection verified. Found existing collections: {collections}")
    except Exception as e:
        print(f"Failed to connect to Qdrant: {e}")