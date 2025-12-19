from qdrant_client import QdrantClient
import os
from dotenv import load_dotenv

load_dotenv()

QDRANT_HOST = os.getenv("QDRANT_HOST")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")

client = QdrantClient(
    url=QDRANT_HOST,
    api_key=QDRANT_API_KEY,
)

print(f"QdrantClient object: {client}")

try:
    # Test if .search exists
    if hasattr(client, 'search'):
        print("'search' method exists on QdrantClient")
    else:
        print("'search' method DOES NOT exist on QdrantClient")
except Exception as e:
    print(f"Error checking 'search' method: {e}")

try:
    # Test if .query.vector_query exists
    if hasattr(client, 'query') and hasattr(client.query, 'vector_query'):
        print("'query.vector_query' method exists on QdrantClient")
    else:
        print("'query.vector_query' method DOES NOT exist on QdrantClient")
except Exception as e:
    print(f"Error checking 'query.vector_query' method: {e}")

print("Qdrant client test complete.")