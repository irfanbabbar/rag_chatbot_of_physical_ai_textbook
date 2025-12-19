import os
from dotenv import load_dotenv
from qdrant_client import models
from vector_db import get_qdrant_client, COLLECTION_NAME
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import TextLoader

load_dotenv()

# --- Configuration ---
# Updated to match your specific file name
BOOK_FILE_PATH = "physical-AI-textbook.txt" 

def index_book_data():
    if not os.path.exists(BOOK_FILE_PATH):
        print(f"Error: file not found at {BOOK_FILE_PATH}")
        return

    print(f"Starting ingestion process for {BOOK_FILE_PATH}...")
    
    # 1. Load and Split Text Document
    loader = TextLoader(BOOK_FILE_PATH, encoding='utf-8')
    data = loader.load()

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=700,
        chunk_overlap=100,
    )
    docs = text_splitter.split_documents(data)
    print(f"Split text into {len(docs)} chunks.")

    # 2. Initialize FREE HuggingFace Embeddings
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    
    qdrant_client = get_qdrant_client()

    # 3. Reset Collection
    qdrant_client.recreate_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=models.VectorParams(size=384, distance=models.Distance.COSINE)
    )
    print(f"Collection '{COLLECTION_NAME}' reset with 384 dimensions.")

    # 4. Generate Embeddings and Upload
    points = []
    print("Generating embeddings...")
    for i, doc in enumerate(docs):
        if not doc.page_content.strip():
            continue
            
        vector = embeddings.embed_query(doc.page_content)
        
        point = models.PointStruct(
            id=i,
            vector=vector,
            payload={
                "text": doc.page_content, 
                "source": BOOK_FILE_PATH
            }
        )
        points.append(point)

    qdrant_client.upsert(
        collection_name=COLLECTION_NAME,
        points=points
    )
    print(f"Done! Successfully uploaded {len(points)} vectors to Qdrant.")

if __name__ == "__main__":
    index_book_data()