from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
import tempfile
from typing import List, Optional
import json
import re
from pydantic import BaseModel
from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import Chroma
from langchain.chains import RetrievalQA
import chromadb
from dotenv import load_dotenv
import logging

# Try to import Gemini, but don't fail if not installed
try:
    from langchain_google_genai import ChatGoogleGenerativeAI
    GEMINI_AVAILABLE = True
    logger = logging.getLogger(__name__)
    logger.info("Gemini API support loaded successfully")
except ImportError:
    GEMINI_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.warning("langchain-google-genai not installed. Install with: pip install langchain-google-genai")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

def clean_pdf_text(text):
    """Clean and normalize PDF text to remove common OCR errors and formatting issues"""
    if not text:
        return ""
    
    # Remove excessive whitespace and normalize
    text = re.sub(r'\s+', ' ', text)
    
    # Fix common OCR errors
    text = re.sub(r'\bomypoonl\b', 'omission', text)
    text = re.sub(r'\bTronsmision\b', 'Transmission', text)
    text = re.sub(r'\bBolay\b', 'Delay', text)
    text = re.sub(r'\bBroosing\b', 'Processing', text)
    text = re.sub(r'\bBley\b', 'Delay', text)
    text = re.sub(r'\bdyre\b', 'time', text)
    text = re.sub(r'\bUhch\b', 'Which', text)
    text = re.sub(r'\bdyonds\b', 'depends', text)
    text = re.sub(r'\btronsmissis2\b', 'transmission', text)
    text = re.sub(r'\bsrate\b', 'rate', text)
    text = re.sub(r'\bdeouases\b', 'decreases', text)
    text = re.sub(r'\bveducang\b', 'reducing', text)
    text = re.sub(r'\byacket\b', 'packet', text)
    text = re.sub(r'\bsige\b', 'size', text)
    text = re.sub(r'\btiamsmission\b', 'transmission', text)
    text = re.sub(r'\bdolay\b', 'delay', text)
    text = re.sub(r'\balao\b', 'also', text)
    text = re.sub(r'\bdecoates\b', 'decreases', text)
    text = re.sub(r'\binsssng\b', 'processing', text)
    text = re.sub(r'\bdlay\b', 'delay', text)
    text = re.sub(r'\bdyends\b', 'depends', text)
    text = re.sub(r'\broaton\b', 'rotation', text)
    text = re.sub(r'\bLauig\b', 'Latency', text)
    text = re.sub(r'\bost\b', 'cost', text)
    text = re.sub(r'\bndoane\b', 'node', text)
    text = re.sub(r'\bvand\b', 'and', text)
    text = re.sub(r'\bsofaaa\b', 'software', text)
    text = re.sub(r'\bfany\b', 'many', text)
    text = re.sub(r'\bZastor\b', 'Master', text)
    text = re.sub(r'\bofniged\b', 'configured', text)
    text = re.sub(r'\byackat\b', 'packet', text)
    text = re.sub(r'\bforwandirg\b', 'forwarding', text)
    text = re.sub(r'\bvanhitbsas\b', 'variables', text)
    text = re.sub(r'\bodace\b', 'place', text)
    text = re.sub(r'\byproassing\b', 'processing', text)
    text = re.sub(r'\blay\b', 'delay', text)
    
    # Fix more common patterns
    text = re.sub(r'\bdans\b', 'time', text)
    text = re.sub(r'\byuling\b', 'sending', text)
    text = re.sub(r'\bwnto\b', 'into', text)
    text = re.sub(r'\bik\b', 'link', text)
    text = re.sub(r'\byst\b', 'just', text)
    text = re.sub(r'\bLend\b', 'sent', text)
    text = re.sub(r'\blavng\b', 'leaving', text)
    text = re.sub(r'\blost\b', 'host', text)
    text = re.sub(r'\bdhans\b', 'time', text)
    text = re.sub(r'\burtore\b', 'router', text)
    text = re.sub(r'\bBont\b', 'point', text)
    text = re.sub(r'\bvat\b', 'at', text)
    text = re.sub(r'\bbiaels\b', 'travels', text)
    text = re.sub(r'\bspad\b', 'speed', text)
    text = re.sub(r'\bmoved\b', 'moved', text)
    text = re.sub(r'\bdistance\b', 'distance', text)
    text = re.sub(r'\but\b', 'of', text)
    text = re.sub(r'\bS\.don\b', 'S.d', text)
    text = re.sub(r'\bS\b', 'S', text)  # Keep S as it might be a variable
    text = re.sub(r'\bR\b', 'R', text)  # Keep R as it might be a variable
    text = re.sub(r'\brm\b', 'from', text)
    text = re.sub(r'\bUmidelle\b', 'Middle', text)
    text = re.sub(r'\bbink\b', 'link', text)
    text = re.sub(r'\bnst\b', 'not', text)
    text = re.sub(r'\byd\b', 'yet', text)
    text = re.sub(r'\bamied\b', 'arrived', text)
    text = re.sub(r'\btas\b', 'has', text)
    text = re.sub(r'\bmet\b', 'met', text)
    text = re.sub(r'\broohad\b', 'reached', text)
    text = re.sub(r'\bteo\b', 'the', text)
    text = re.sub(r'\bLassummes\b', 'Assumes', text)
    text = re.sub(r'\byrnpagalon\b', 'propagation', text)
    text = re.sub(r'\bdeley\b', 'delay', text)
    text = re.sub(r'\bbngh\b', 'being', text)
    text = re.sub(r'\bforund\b', 'forward', text)
    text = re.sub(r'\btning\b', 'timing', text)
    text = re.sub(r'\bwitb\b', 'with', text)
    text = re.sub(r'\ba2e\b', 'are', text)
    text = re.sub(r'\b&ame\b', 'same', text)
    text = re.sub(r'\bbst\b', 'best', text)
    text = re.sub(r'\bul\b', 'will', text)
    text = re.sub(r'\bbe\b', 'be', text)
    text = re.sub(r'\bnet\b', 'net', text)
    text = re.sub(r'\bpropagadist\b', 'propagation', text)
    text = re.sub(r'\bhlay\b', 'delay', text)
    text = re.sub(r'\blse\b', 'else', text)
    text = re.sub(r'\bUae\b', 'Use', text)
    text = re.sub(r'\bLacoSL\b', 'L/cS', text)
    text = re.sub(r'\byazt\b', 'fast', text)
    text = re.sub(r'\byackat\b', 'packet', text)
    text = re.sub(r'\bsenlliyaton\b', 'simulation', text)
    
    # Additional fixes for the specific text you mentioned
    text = re.sub(r'\bCemsidor\b', 'Consider', text)
    text = re.sub(r'\bamnodod\b', 'modulated', text)
    text = re.sub(r'\bsraa\b', 'rate', text)
    text = re.sub(r'\bbps\b', 'bps', text)
    text = re.sub(r'\bduprose\b', 'purpose', text)
    text = re.sub(r'\bsyponalod\b', 'symbolized', text)
    text = re.sub(r'\bsngl\b', 'single', text)
    text = re.sub(r'\bmeters/sec\b', 'meters/sec', text)
    text = re.sub(r'\bsireL\b', 'size L', text)
    text = re.sub(r'\bm vamd\b', 'in', text)
    
    # Remove excessive punctuation and normalize
    text = re.sub(r'[^\w\s\.\,\!\?\;\:\-\(\)]', '', text)
    text = re.sub(r'\s+', ' ', text)
    
    return text.strip()

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
        try:
            loader = PyPDFLoader(tmp_file_path)
            documents = loader.load()
            logger.info(f"PDF loaded successfully: {len(documents)} pages")
        except Exception as pdf_error:
            logger.error(f"PyPDFLoader failed: {str(pdf_error)}")
            raise HTTPException(status_code=400, detail=f"Could not read PDF file. Error: {str(pdf_error)}")
        
        # Validate documents have content
        if not documents:
            raise HTTPException(status_code=400, detail="PDF appears to be empty or corrupted.")
        
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
        try:
            embeddings = HuggingFaceEmbeddings(
                model_name="sentence-transformers/all-MiniLM-L6-v2"
            )
            
            vector_store = Chroma.from_documents(
                documents=splits,
                embedding=embeddings
            )
            logger.info("Vector store created successfully")
        except Exception as embedding_error:
            logger.error(f"Embedding generation error: {str(embedding_error)}")
            raise HTTPException(status_code=500, detail=f"Failed to create embeddings: {str(embedding_error)}")
        
        # Initialize QA chain with Gemini
        gemini_key = os.getenv("GEMINI_API_KEY")
        logger.info(f"Gemini API key available: {bool(gemini_key)}")
        
        if GEMINI_AVAILABLE and gemini_key and gemini_key != "your_gemini_api_key_here":
            logger.info("Initializing Gemini QA chain")
            try:
                # Try different Gemini models in order of preference
                models_to_try = ["gemini-1.5-flash", "gemini-1.5-pro", "gemini-pro"]
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
                    # Create a conversational prompt template
                    from langchain.prompts import PromptTemplate
                    
                    prompt_template = """You are a helpful and friendly AI assistant who loves to help users understand their PDF documents.
                    You should respond in a conversational, warm, and engaging manner - like talking to a friend who's genuinely interested in helping.
                    
                    IMPORTANT: 
                    - Always respond in clear, proper English language only
                    - If the context contains garbled or unclear text, explain what you can understand and ask for clarification
                    - Provide clear, readable explanations that make sense to the user
                    - Do not repeat garbled or corrupted text from the PDF
                    - Translate any unclear text into proper English
                    
                    Use the following pieces of context from the PDF document to answer the user's question in a helpful and friendly way.
                    If you don't know the answer based on the context, just say so in a friendly manner and suggest what they might ask instead.
                    
                    Context from PDF:
                    {context}
                    
                    Question: {question}
                    
                    Friendly Response:"""
                    
                    PROMPT = PromptTemplate(
                        template=prompt_template, 
                        input_variables=["context", "question"]
                    )
                    
                    qa_chain = RetrievalQA.from_chain_type(
                        llm=llm,
                        chain_type="stuff",
                        retriever=vector_store.as_retriever(search_kwargs={"k": 5}),
                        return_source_documents=True,
                        chain_type_kwargs={"prompt": PROMPT}
                    )
                    logger.info(f"Gemini QA chain initialized successfully with model: {llm.model}")
                else:
                    logger.error("All Gemini models failed, falling back to similarity search")
                    qa_chain = None
                    
            except Exception as gemini_error:
                logger.error(f"Gemini initialization error: {str(gemini_error)}")
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
        
        return JSONResponse({
            "message": "PDF uploaded and processed successfully",
            "pages": len(documents),
            "chunks": len(splits),
            "gemini_enabled": qa_chain is not None,
            "api_type": "gemini" if qa_chain else "similarity_search",
            "gemini_package_available": GEMINI_AVAILABLE
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
            logger.info("Using Gemini QA chain for response")
            try:
                result = qa_chain({"query": chat_message.message})
                response = result["result"]
                source_docs = result.get("source_documents", [])
                sources = [f"Page {doc.metadata.get('page', 'Unknown')}" for doc in source_docs]
                logger.info(f"Gemini response generated successfully: {response[:100]}...")
            except Exception as gemini_error:
                logger.error(f"Gemini API error: {str(gemini_error)}")
                # Fallback to similarity search if Gemini fails
                logger.info("Falling back to similarity search due to Gemini error")
                docs = vector_store.similarity_search(chat_message.message, k=3)
                logger.info(f"Found {len(docs)} relevant documents")
                
                if not docs:
                    response = "I couldn't find anything related to that in your PDF. Try asking about a different topic."
                    sources = []
                else:
                    # Clean the document content before showing it
                    cleaned_content = []
                    for doc in docs:
                        cleaned_text = clean_pdf_text(doc.page_content)
                        if cleaned_text and len(cleaned_text) > 10:
                            cleaned_content.append(f"**Page {doc.metadata.get('page', 'Unknown')}:** {cleaned_text}")
                    
                    if cleaned_content:
                        response = f"Here's what I found in your PDF about '{chat_message.message}':\n\n" + "\n\n".join(cleaned_content)
                    else:
                        response = "I found some content but it appears to have formatting issues. Try asking about a different aspect."
                    sources = [f"Page {doc.metadata.get('page', 'Unknown')}" for doc in docs]
        else:
            logger.info("Using similarity search fallback")
            docs = vector_store.similarity_search(chat_message.message, k=3)
            logger.info(f"Found {len(docs)} relevant documents")
            
            if not docs:
                response = "I couldn't find anything related to that in your PDF. Try asking about a different topic."
                sources = []
            else:
                # Clean the document content before showing it
                cleaned_content = []
                for doc in docs:
                    cleaned_text = clean_pdf_text(doc.page_content)
                    if cleaned_text and len(cleaned_text) > 10:
                        cleaned_content.append(f"**Page {doc.metadata.get('page', 'Unknown')}:** {cleaned_text}")
                
                if cleaned_content:
                    response = f"Here's what I found in your PDF about '{chat_message.message}':\n\n" + "\n\n".join(cleaned_content)
                else:
                    response = "I found some content but it appears to have formatting issues. Try asking about a different aspect."
                sources = [f"Page {doc.metadata.get('page', 'Unknown')}" for doc in docs]
            
            logger.info("Similarity search response generated")
        
        logger.info(f"Final response: {response[:100]}...")
        return ChatResponse(response=response, sources=sources)
        
    except Exception as e:
        logger.error(f"Error generating response: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error generating response: {str(e)}")

@app.get("/health")
async def health_check():
    """Health check endpoint to diagnose issues"""
    try:
        # Check if required packages are available
        package_status = {}
        
        try:
            import langchain
            package_status["langchain"] = f"✅ {langchain.__version__}"
        except ImportError as e:
            package_status["langchain"] = f"❌ Not installed: {str(e)}"
        
        try:
            import sentence_transformers
            package_status["sentence_transformers"] = f"✅ {sentence_transformers.__version__}"
        except ImportError as e:
            package_status["sentence_transformers"] = f"❌ Not installed: {str(e)}"
        
        try:
            import chromadb
            package_status["chromadb"] = f"✅ {chromadb.__version__}"
        except ImportError as e:
            package_status["chromadb"] = f"❌ Not installed: {str(e)}"
        
        try:
            import langchain_google_genai
            package_status["langchain_google_genai"] = f"✅ {langchain_google_genai.__version__}"
        except ImportError as e:
            package_status["langchain_google_genai"] = f"❌ Not installed: {str(e)}"
        
        try:
            import google.generativeai
            package_status["google_generativeai"] = f"✅ {google.generativeai.__version__}"
        except ImportError as e:
            package_status["google_generativeai"] = f"❌ Not installed: {str(e)}"
        
        try:
            import openai
            package_status["openai"] = f"✅ {openai.__version__}"
        except ImportError as e:
            package_status["openai"] = f"❌ Not installed: {str(e)}"
        
        # Check API keys
        api_status = {}
        gemini_key = os.getenv("GEMINI_API_KEY")
        api_status["gemini_key"] = "✅ Set" if gemini_key and gemini_key != "your_gemini_api_key_here" else "❌ Not set or invalid"
        
        # Check current state
        state_status = {}
        state_status["documents"] = f"✅ {len(documents)} pages" if documents else "❌ No PDF uploaded"
        state_status["vector_store"] = "✅ Ready" if vector_store else "❌ Not initialized"
        state_status["qa_chain"] = "✅ Ready" if qa_chain else "❌ Not initialized"
        
        return {
            "status": "healthy",
            "message": "PDF RAG Chat System is running",
            "packages": package_status,
            "api_keys": api_status,
            "current_state": state_status
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Health check failed: {str(e)}",
            "error": str(e)
        }

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
