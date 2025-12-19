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

import os
import shutil
import ssl  # Added for SSL fix
from dotenv import load_dotenv
from fastapi import FastAPI, Request, HTTPException, UploadFile, File
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import List

# --- SSL Fix ---
# This bypasses certificate verification for local environments
ssl._create_default_https_context = ssl._create_unverified_context

# --- LangChain & AI Imports ---
from langchain_groq import ChatGroq 
from langchain_huggingface import HuggingFaceEmbeddings 
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

# Import your custom Qdrant settings
from vector_db import get_qdrant_client, COLLECTION_NAME

# Load environment variables
load_dotenv()

# --- Configuration ---
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
CHAT_MODEL = "llama-3.3-70b-versatile" 

if not GROQ_API_KEY:
    raise ValueError("Error: GROQ_API_KEY is missing from .env file.")

# --- Initialize AI Clients ---
print("Initializing AI clients...")
try:
    qdrant_client = get_qdrant_client()
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    
    chat_llm = ChatGroq(
        groq_api_key=GROQ_API_KEY, 
        model_name=CHAT_MODEL, 
        temperature=0
    )
    print("AI clients initialized successfully.")
except Exception as e:
    print(f"Error initializing clients: {e}")
    raise e

# --- FastAPI Setup ---
app = FastAPI(title="Physical AI RAG Chatbot")
templates = Jinja2Templates(directory="templates")

class QueryRequest(BaseModel):
    question: str

class QueryResponse(BaseModel):
    answer: str
    sources: List[str] = []

# --- Routes ---

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/upload-pdf")
async def upload_pdf(file: UploadFile = File(...)):
    """Handles PDF upload, splits text, and stores vectors in Qdrant."""
    temp_path = f"temp_{file.filename}"
    try:
        # 1. Save file temporarily
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # 2. Load and Split PDF
        loader = PyPDFLoader(temp_path)
        docs = loader.load()
        
        # Split text into 1000-character chunks
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
        chunks = text_splitter.split_documents(docs)

        # 3. Create Vectors and Upload to Qdrant
        points = []
        for i, chunk in enumerate(chunks):
            vector = embeddings.embed_query(chunk.page_content)
            points.append({
                "id": os.urandom(16).hex(),
                "vector": vector,
                "payload": {
                    "text": chunk.page_content, 
                    "source": file.filename
                }
            })
        
        # Batch upload to Qdrant
        qdrant_client.upsert(collection_name=COLLECTION_NAME, points=points)
        
        return {"message": f"Successfully indexed {len(chunks)} sections from {file.filename}!"}

    except Exception as e:
        print(f"Upload Error: {e}")
        return {"message": f"Error processing PDF: {str(e)}"}
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

@app.post("/query", response_model=QueryResponse)
async def query_knowledge_base(query: QueryRequest):
    question_text = query.question.strip()
    if not question_text:
        raise HTTPException(status_code=400, detail="Empty query.")

    try:
        # 1. Search Qdrant for relevant context
        query_vector = embeddings.embed_query(question_text)
        response = qdrant_client.query_points(
            collection_name=COLLECTION_NAME,
            query=query_vector,
            limit=5 
        )
        
        if not response.points:
            return QueryResponse(answer="I couldn't find any relevant information.", sources=[])

        # 2. Build context
        context_text = ""
        sources_list = set()
        for pt in response.points:
            context_text += f"\n---\n{pt.payload['text']}\n"
            sources_list.add(pt.payload.get('source', 'Unknown'))

        # 3. Generate Answer
        system_prompt = f"""You are a Physical AI expert. Answer the question strictly using the context. 
        If the answer isn't there, say you don't know.
        Context: {context_text}"""

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=question_text)
        ]

        ai_response = chat_llm.invoke(messages)
        return QueryResponse(answer=ai_response.content, sources=list(sources_list))

    except Exception as e:
        print(f"Query Error: {e}")
        return QueryResponse(answer="Internal server error.", sources=[])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=3000, reload=True)