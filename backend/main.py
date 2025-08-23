from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
import tempfile
from typing import List, Optional
import json
from pydantic import BaseModel
from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import Chroma
from langchain.chains import RetrievalQA
from langchain.llms import OpenAI
import chromadb
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="PDF RAG Chat System", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variables for document storage
documents = []
vector_store = None
qa_chain = None

class ChatMessage(BaseModel):
    message: str
    user_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    sources: List[str] = []

@app.post("/upload-pdf")
async def upload_pdf(file: UploadFile = File(...)):
    """Upload and process PDF file"""
    global documents, vector_store, qa_chain
    
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")
    
    try:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            content = await file.read()
            tmp_file.write(content)
            tmp_file_path = tmp_file.name
        
        # Load and process PDF
        loader = PyPDFLoader(tmp_file_path)
        documents = loader.load()
        
        # Split documents into chunks
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )
        splits = text_splitter.split_documents(documents)
        
        # Create embeddings and vector store
        embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
        
        vector_store = Chroma.from_documents(
            documents=splits,
            embedding=embeddings
        )
        
        # Initialize QA chain
        if os.getenv("OPENAI_API_KEY"):
            llm = OpenAI(temperature=0)
            qa_chain = RetrievalQA.from_chain_type(
                llm=llm,
                chain_type="stuff",
                retriever=vector_store.as_retriever(search_kwargs={"k": 3})
            )
        
        # Clean up temporary file
        os.unlink(tmp_file_path)
        
        return JSONResponse({
            "message": "PDF uploaded and processed successfully",
            "pages": len(documents),
            "chunks": len(splits)
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing PDF: {str(e)}")

@app.post("/chat")
async def chat(chat_message: ChatMessage):
    """Chat with the PDF content"""
    global qa_chain, vector_store
    
    if not vector_store:
        raise HTTPException(status_code=400, detail="No PDF uploaded yet")
    
    try:
        if qa_chain:
            # Use OpenAI if available
            response = qa_chain.run(chat_message.message)
            sources = []
        else:
            # Fallback to vector similarity search
            docs = vector_store.similarity_search(chat_message.message, k=3)
            response = "Based on the PDF content:\n\n" + "\n\n".join([doc.page_content for doc in docs])
            sources = [f"Page {doc.metadata.get('page', 'Unknown')}" for doc in docs]
        
        return ChatResponse(response=response, sources=sources)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating response: {str(e)}")

@app.get("/pdf-info")
async def get_pdf_info():
    """Get information about the uploaded PDF"""
    if not documents:
        return {"message": "No PDF uploaded"}
    
    return {
        "pages": len(documents),
        "filename": "uploaded_document.pdf"
    }

@app.post("/save-annotation")
async def save_annotation(annotation_data: dict):
    """Save whiteboard annotations"""
    # In a real application, you'd save this to a database
    # For now, we'll just return success
    return {"message": "Annotation saved successfully", "data": annotation_data}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
