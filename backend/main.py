from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
import tempfile
from typing import List, Optional
import json
import logging
from pydantic import BaseModel
from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import Chroma
from langchain.chains import RetrievalQA
import chromadb
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Try to import Gemini, but don't fail if not installed
try:
    from langchain_google_genai import ChatGoogleGenerativeAI
    GEMINI_AVAILABLE = True
    logger.info("Gemini API support loaded successfully")
except ImportError:
    GEMINI_AVAILABLE = False
    logger.warning("langchain_google_genai not installed. Install with: pip install langchain-google-genai")

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
    
    logger.info(f"Received PDF upload request: {file.filename}")
    
    if not file.filename.endswith('.pdf'):
        logger.error(f"Invalid file type: {file.filename}")
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")
    
    try:
        # Save uploaded file temporarily
        logger.info("Saving uploaded file temporarily")
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            content = await file.read()
            tmp_file.write(content)
            tmp_file_path = tmp_file.name
        
        logger.info(f"Temporary file saved: {tmp_file_path}")
        
        # Load and process PDF
        logger.info("Loading PDF with PyPDFLoader")
        loader = PyPDFLoader(tmp_file_path)
        documents = loader.load()
        logger.info(f"PDF loaded successfully: {len(documents)} pages")
        
        # Split documents into chunks
        logger.info("Splitting documents into chunks")
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )
        splits = text_splitter.split_documents(documents)
        logger.info(f"Documents split into {len(splits)} chunks")
        
        # Create embeddings and vector store
        logger.info("Creating embeddings and vector store")
        embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
        
        vector_store = Chroma.from_documents(
            documents=splits,
            embedding=embeddings
        )
        logger.info("Vector store created successfully")
        
        # Initialize QA chain with Gemini
        gemini_key = os.getenv("GEMINI_API_KEY")
        
        if GEMINI_AVAILABLE and gemini_key and gemini_key != "your_gemini_api_key_here":
            logger.info("Initializing Gemini QA chain")
            try:
                # Try different Gemini models in order of preference
                # gemini-2.0-flash-exp: Latest experimental model (Gemini 2.5 Flash equivalent)
                # gemini-1.5-flash: Fast and efficient
                # gemini-1.5-pro: Most capable for complex tasks
                models_to_try = ["gemini-2.0-flash-exp", "gemini-1.5-flash", "gemini-1.5-pro"]
                llm = None
                
                for model_name in models_to_try:
                    try:
                        logger.info(f"Trying Gemini model: {model_name}")
                        llm = ChatGoogleGenerativeAI(
                            model=model_name,
                            google_api_key=gemini_key,
                            temperature=0
                        )
                        logger.info(f"Successfully initialized Gemini model: {model_name}")
                        break
                    except Exception as model_error:
                        logger.warning(f"Failed to initialize {model_name}: {str(model_error)}")
                        continue
                
                if llm:
                    qa_chain = RetrievalQA.from_chain_type(
                        llm=llm,
                        chain_type="stuff",
                        retriever=vector_store.as_retriever(search_kwargs={"k": 3})
                    )
                    logger.info(f"Gemini QA chain initialized successfully with model: {llm.model}")
                else:
                    logger.error("All Gemini models failed, falling back to similarity search")
                    qa_chain = None
                    
            except Exception as e:
                logger.error(f"Error initializing Gemini QA chain: {str(e)}")
                qa_chain = None
        else:
            if not GEMINI_AVAILABLE:
                logger.info("Gemini package not available, using similarity search fallback")
            else:
                logger.info("No Gemini API key found, using similarity search fallback")
            qa_chain = None
        
        # Clean up temporary file
        os.unlink(tmp_file_path)
        logger.info("Temporary file cleaned up")
        
        # Determine if Gemini API is enabled
        api_enabled = GEMINI_AVAILABLE and gemini_key and gemini_key != "your_gemini_api_key_here"
        
        # Get the model name if available
        model_name = "unknown"
        if qa_chain and hasattr(qa_chain, 'llm') and hasattr(qa_chain.llm, 'model'):
            model_name = qa_chain.llm.model
        
        return JSONResponse({
            "message": "PDF uploaded and processed successfully",
            "pages": len(documents),
            "chunks": len(splits),
            "gemini_enabled": api_enabled,
            "api_type": "gemini" if api_enabled else "similarity_search",
            "gemini_package_available": GEMINI_AVAILABLE,
            "model_name": model_name
        })
        
    except Exception as e:
        logger.error(f"Error processing PDF: {str(e)}", exc_info=True)
        # Clean up temporary file if it exists
        if 'tmp_file_path' in locals():
            try:
                os.unlink(tmp_file_path)
            except:
                pass
        raise HTTPException(status_code=500, detail=f"Error processing PDF: {str(e)}")

@app.post("/chat")
async def chat(chat_message: ChatMessage):
    """Chat with the PDF content"""
    global qa_chain, vector_store
    
    logger.info(f"Received chat message: {chat_message.message[:100]}...")
    
    if not vector_store:
        logger.error("No PDF uploaded yet")
        raise HTTPException(status_code=400, detail="No PDF uploaded yet. Please upload a PDF first.")
    
    try:
        if qa_chain:
            # Use Gemini if available
            logger.info("Using Gemini QA chain for response")
            try:
                response = qa_chain.run(chat_message.message)
                sources = []
                logger.info("Gemini response generated successfully")
            except Exception as gemini_error:
                logger.error(f"Gemini API error: {str(gemini_error)}")
                # Fallback to similarity search if Gemini fails
                logger.info("Falling back to similarity search due to Gemini error")
                docs = vector_store.similarity_search(chat_message.message, k=3)
                if not docs:
                    response = "I encountered an error with the AI service. Please try again or rephrase your question."
                    sources = []
                else:
                    response = "Based on the PDF content:\n\n" + "\n\n".join([doc.page_content for doc in docs])
                    sources = [f"Page {doc.metadata.get('page', 'Unknown')}" for doc in docs]
        else:
            # Fallback to vector similarity search
            logger.info("Using similarity search fallback")
            docs = vector_store.similarity_search(chat_message.message, k=3)
            logger.info(f"Found {len(docs)} relevant documents")
            
            if not docs:
                response = "I couldn't find relevant information in the PDF to answer your question. Please try rephrasing your question or ask about a different topic."
                sources = []
            else:
                response = "Based on the PDF content:\n\n" + "\n\n".join([doc.page_content for doc in docs])
                sources = [f"Page {doc.metadata.get('page', 'Unknown')}" for doc in docs]
            
            logger.info("Similarity search response generated")
        
        return ChatResponse(response=response, sources=sources)
        
    except Exception as e:
        logger.error(f"Error generating response: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error generating response: {str(e)}")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "message": "PDF RAG Chat System is running"}

@app.get("/pdf-info")
async def get_pdf_info():
    """Get information about the uploaded PDF"""
    global documents, vector_store, qa_chain
    
    if not documents:
        return {"message": "No PDF uploaded", "status": "no_pdf"}
    
    # Check if Gemini API is configured
    gemini_key = os.getenv("GEMINI_API_KEY")
    
    api_enabled = GEMINI_AVAILABLE and gemini_key and gemini_key != "your_gemini_api_key_here"
    
    # Get the model name if available
    model_name = "unknown"
    if qa_chain and hasattr(qa_chain, 'llm') and hasattr(qa_chain.llm, 'model'):
        model_name = qa_chain.llm.model
    
    return {
        "pages": len(documents),
        "filename": "uploaded_document.pdf",
        "vector_store_ready": vector_store is not None,
        "gemini_enabled": api_enabled,
        "api_type": "gemini" if api_enabled else "similarity_search",
        "gemini_package_available": GEMINI_AVAILABLE,
        "model_name": model_name,
        "status": "ready"
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
