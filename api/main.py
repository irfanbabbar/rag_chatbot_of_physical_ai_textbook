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
# backend/main.py
import os
import shutil
import ssl
from dotenv import load_dotenv
from fastapi import FastAPI, Request, HTTPException, UploadFile, File
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import List

# --- LangChain & AI Imports ---
from langchain_groq import ChatGroq 
from langchain_huggingface import HuggingFaceEmbeddings 
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

# Import your custom Qdrant settings
# Use the dot (.) for relative import
from .vector_db import get_qdrant_client, COLLECTION_NAME

# Load environment variables
load_dotenv()

# --- SSL Fix ---
ssl._create_default_https_context = ssl._create_unverified_context

# --- FastAPI Setup ---
app = FastAPI(title="Physical AI RAG Chatbot")

# FIXED: Dynamic path to find 'templates' folder from the 'api' directory
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(current_dir)
templates = Jinja2Templates(directory=os.path.join(root_dir, "templates"))

# --- Configuration ---
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
CHAT_MODEL = "llama-3.3-70b-versatile" 

# --- Initialize AI Clients ---
print("Initializing AI clients...")
try:
    qdrant_client = get_qdrant_client()
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    chat_llm = ChatGroq(groq_api_key=GROQ_API_KEY, model_name=CHAT_MODEL, temperature=0)
except Exception as e:
    print(f"Init Error: {e}")

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
    temp_path = f"/tmp/{file.filename}" # Use /tmp/ for Vercel write access
    try:
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        loader = PyPDFLoader(temp_path)
        docs = loader.load()
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
        chunks = text_splitter.split_documents(docs)

        points = []
        for i, chunk in enumerate(chunks):
            vector = embeddings.embed_query(chunk.page_content)
            points.append({
                "id": os.urandom(16).hex(),
                "vector": vector,
                "payload": {"text": chunk.page_content, "source": file.filename}
            })
        
        qdrant_client.upsert(collection_name=COLLECTION_NAME, points=points)
        return {"message": f"Successfully indexed {len(chunks)} sections!"}
    except Exception as e:
        return {"message": f"Error: {str(e)}"}
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

@app.post("/query", response_model=QueryResponse)
async def query_knowledge_base(query: QueryRequest):
    try:
        query_vector = embeddings.embed_query(query.question)
        response = qdrant_client.query_points(collection_name=COLLECTION_NAME, query=query_vector, limit=5)
        
        if not response.points:
            return QueryResponse(answer="No relevant info found.", sources=[])

        context_text = "\n".join([pt.payload['text'] for pt in response.points])
        sources = list(set([pt.payload.get('source', 'Unknown') for pt in response.points]))

        system_prompt = f"Answer using context only: {context_text}"
        messages = [SystemMessage(content=system_prompt), HumanMessage(content=query.question)]
        ai_res = chat_llm.invoke(messages)
        
        return QueryResponse(answer=ai_res.content, sources=sources)
    except Exception as e:
        return QueryResponse(answer=f"Error: {str(e)}", sources=[])

# Local run (Vercel ignores this)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=3000)