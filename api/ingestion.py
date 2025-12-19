import os
import glob
import markdown
import tiktoken
import re
import hashlib
from qdrant_client import QdrantClient, models
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# Configuration
QDRANT_HOST = os.getenv("QDRANT_HOST")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
COLLECTION_NAME = "textbook_chunks"
DOCS_PATH = "/home/aza_comp/physical-ai-textbook/textbook-site/docs"
EMBEDDING_MODEL = "text-embedding-ada-002"
CHUNK_SIZE = 1000  # tokens
CHUNK_OVERLAP = 200 # tokens

client = QdrantClient(
    url=QDRANT_HOST,
    api_key=QDRANT_API_KEY,
)
openai_client = OpenAI(api_key=OPENAI_API_KEY)
tokenizer = tiktoken.encoding_for_model(EMBEDDING_MODEL)

def get_markdown_files(path):
    """Recursively get all markdown files from a given path."""
    return glob.glob(os.path.join(path, '**/*.md'), recursive=True)

def chunk_text(text, chunk_size, chunk_overlap):
    """
    Splits text into chunks of tokens with overlap.
    """
    tokens = tokenizer.encode(text)
    chunks = []
    for i in range(0, len(tokens), chunk_size - chunk_overlap):
        chunk = tokens[i : i + chunk_size]
        chunks.append(tokenizer.decode(chunk))
    return chunks

def get_embedding(text):
    """Generates an embedding for the given text using OpenAI."""
    response = openai_client.embeddings.create(
        input=text,
        model=EMBEDDING_MODEL
    )
    return response.data[0].embedding

def upload_to_qdrant(file_path, chunks):
    """Uploads text chunks and their embeddings to Qdrant."""
    points = []
    for i, chunk in enumerate(chunks):
        embedding = get_embedding(chunk)
        points.append(
            models.PointStruct(
                id=int(hashlib.sha256(f"{file_path}_{i}".encode()).hexdigest(), 16) % (2**63 - 1),
                vector=embedding,
                payload={"text": chunk, "source": file_path}
            )
        )

    # Ensure collection exists and is configured correctly
    if not client.collection_exists(collection_name=COLLECTION_NAME):
        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=models.VectorParams(size=len(points[0].vector), distance=models.Distance.COSINE),
        )
        print(f"Collection {COLLECTION_NAME} created.")
    else:
        print(f"Collection {COLLECTION_NAME} already exists. Skipping creation.")

    client.upsert(
        collection_name=COLLECTION_NAME,
        points=points,
        wait=True
    )
    print(f"Uploaded {len(points)} chunks from {file_path} to Qdrant.")

def main():
    markdown_files = get_markdown_files(DOCS_PATH)
    print(f"Found {len(markdown_files)} markdown files.")

    for file_path in markdown_files:
        with open(file_path, 'r', encoding='utf-8') as f:
            md_content = f.read()

        # Convert markdown to plain text for embedding (optional, but often better for RAG)
        plain_text = markdown.markdown(md_content, extensions=['fenced_code', 'tables'])
        # Further clean up HTML tags if any remain from markdown conversion
        plain_text = ' '.join(plain_text.splitlines())
        plain_text = re.sub(r'<[^>]+>', '', plain_text) # Remove remaining HTML tags

        chunks = chunk_text(plain_text, CHUNK_SIZE, CHUNK_OVERLAP)
        upload_to_qdrant(file_path, chunks)
    print("Content ingestion complete.")

if __name__ == "__main__":
    main()
