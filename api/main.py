# import os
# from fastapi import FastAPI, HTTPException
# from fastapi.middleware.cors import CORSMiddleware
# from pydantic import BaseModel
# from qdrant_client import QdrantClient
# from openai import OpenAI
# from dotenv import load_dotenv

# # Load environment variables
# load_dotenv()

# # Configuration
# QDRANT_HOST = os.getenv("QDRANT_HOST")
# QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
# OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
# COLLECTION_NAME = "textbook-site"
# EMBEDDING_MODEL = "text-embedding-ada-002"
# GPT_MODEL = "gpt-4o-mini"

# # Initialize clients
# app = FastAPI()

# # Set up CORS middleware
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["https://textbook-site.vercel.app"],  # Allow your Docusaurus development server
#     allow_credentials=True,
#     allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
#     allow_headers=["X-API-Key", "Content-Type", "Authorization"],
# )

# try:
#     qdrant_client = QdrantClient(
#         url=QDRANT_HOST,
#         api_key=QDRANT_API_KEY,
#     )
#     openai_client = OpenAI(api_key=OPENAI_API_KEY)
# except Exception as e:
#     raise RuntimeError(f"Failed to initialize clients: {e}")

# class Query(BaseModel):
#     question: str
#     selected_text: str = None

# def get_embedding(text):
#     """Generates an embedding for the given text using OpenAI."""
#     response = openai_client.embeddings.create(
#         input=text,
#         model=EMBEDDING_MODEL
#     )
#     return response.data[0].embedding

# @app.post("/ask")
# async def ask_question(query: Query):
#     try:
#         # 1. Generate embedding for the user's question (and selected text)
#         query_text = f"User question: {query.question}"
#         if query.selected_text:
#             query_text = f"Context from selected text: {query.selected_text}. {query_text}"

#         query_embedding = get_embedding(query_text)

#         # 2. Retrieve relevant context from Qdrant
#         search_result = qdrant_client.query.vector_query(
#             collection_name=COLLECTION_NAME,
#             query_vector=query_embedding,
#             limit=3,  # Retrieve top 3 relevant chunks
#             using="vector" # Specify the vector name if you have multiple, "vector" is default
#         )

#         context = "\n".join([hit.payload["text"] for hit in search_result])
#         sources = [hit.payload["source"] for hit in search_result]

#         # 3. Formulate prompt for OpenAI
#         messages = [
#             {"role": "system", "content": "You are a helpful assistant for a textbook. Answer the user's question based ONLY on the provided context. If you cannot find the answer, state that you don't know. Cite the source files if applicable."},
#             {"role": "user", "content": f"Context: {context}\n\nQuestion: {query.question}"}
#         ]

#         # 4. Get response from OpenAI
#         openai_response = openai_client.chat.completions.create(
#             model=GPT_MODEL,
#             messages=messages,
#         )

#         answer = openai_response.choices[0].message.content

#         return {"answer": answer, "sources": list(set(sources))}

#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

# @app.get("/")
# async def root():
#     return {"message": "RAG Chatbot FastAPI is running!"}

# api/main.py
import os
import shutil
import ssl
from dotenv import load_dotenv
from fastapi import FastAPI, Request, HTTPException, UploadFile, File
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List

# --- LangChain & AI Imports ---
from langchain_groq import ChatGroq 
from langchain_huggingface import HuggingFaceEmbeddings 
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

# FIXED: Import vector_db directly (not relative import)
try:
    from api.vector_db import get_qdrant_client, COLLECTION_NAME
except ImportError:
    from vector_db import get_qdrant_client, COLLECTION_NAME

# Load environment variables
load_dotenv()

# --- SSL Fix ---
ssl._create_default_https_context = ssl._create_unverified_context

# --- FastAPI Setup ---
app = FastAPI(
    title="Physical AI RAG Chatbot",
    description="RAG-based chatbot for Physical AI Textbook",
    version="1.0.0"
)

# Add CORS for frontend access
from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Global Client Variables (Lazy Init) ---
_qdrant_client = None
_embeddings = None
_chat_llm = None

def get_clients():
    """Lazy initialization of AI clients to avoid Vercel boot timeouts."""
    global _qdrant_client, _embeddings, _chat_llm
    
    if _qdrant_client is None:
        _qdrant_client = get_qdrant_client()
    
    if _embeddings is None:
        # Note: This is a heavy model (100MB+). It will load on first request.
        _embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    
    if _chat_llm is None:
        GROQ_API_KEY = os.getenv("GROQ_API_KEY")
        if not GROQ_API_KEY:
            raise ValueError("GROQ_API_KEY not found in environment variables")
        _chat_llm = ChatGroq(
            groq_api_key=GROQ_API_KEY, 
            model_name="llama-3.3-70b-versatile", 
            temperature=0
        )
        
    return _qdrant_client, _embeddings, _chat_llm

class QueryRequest(BaseModel):
    question: str

class QueryResponse(BaseModel):
    answer: str
    sources: List[str] = []

# --- Routes ---

@app.get("/")
async def root():
    """Root endpoint with API info"""
    return {
        "status": "success",
        "message": "Physical AI Textbook RAG Chatbot API",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "upload": "/upload-pdf (POST)",
            "query": "/query (POST)",
            "docs": "/docs"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "RAG Chatbot API"
    }

@app.post("/upload-pdf")
async def upload_pdf(file: UploadFile = File(...)):
    """Upload and index a PDF document"""
    temp_path = f"/tmp/{file.filename}"
    try:
        q_client, embs, _ = get_clients()
        
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        loader = PyPDFLoader(temp_path)
        docs = loader.load()
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000, 
            chunk_overlap=100
        )
        chunks = text_splitter.split_documents(docs)

        points = []
        for i, chunk in enumerate(chunks):
            vector = embs.embed_query(chunk.page_content)
            points.append({
                "id": os.urandom(16).hex(),
                "vector": vector,
                "payload": {
                    "text": chunk.page_content, 
                    "source": file.filename
                }
            })
        
        q_client.upsert(collection_name=COLLECTION_NAME, points=points)
        return {
            "status": "success",
            "message": f"Successfully indexed {len(chunks)} sections from {file.filename}"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing PDF: {str(e)}")
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

@app.post("/query", response_model=QueryResponse)
async def query_knowledge_base(query: QueryRequest):
    """Query the knowledge base with a question"""
    try:
        q_client, embs, llm = get_clients()
        
        query_vector = embs.embed_query(query.question)
        response = q_client.query_points(
            collection_name=COLLECTION_NAME, 
            query=query_vector, 
            limit=5
        )
        
        if not response.points:
            return QueryResponse(
                answer="No relevant information found in the knowledge base.",
                sources=[]
            )

        context_text = "\n\n".join([
            pt.payload['text'] for pt in response.points
        ])
        sources = list(set([
            pt.payload.get('source', 'Unknown') 
            for pt in response.points
        ]))

        system_prompt = (
            "You are a helpful AI assistant. Answer the user's question "
            "based only on the following context. If the answer is not in "
            "the context, say so.\n\nContext:\n" + context_text
        )
        messages = [
            SystemMessage(content=system_prompt), 
            HumanMessage(content=query.question)
        ]
        ai_res = llm.invoke(messages)
        
        return QueryResponse(
            answer=ai_res.content, 
            sources=sources
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error querying: {str(e)}")

# For local development
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=3000)
