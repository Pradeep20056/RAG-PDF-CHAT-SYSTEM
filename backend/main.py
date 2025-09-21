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
conversation_history = []  # Store conversation context

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
            # Try alternative PDF loading method
            try:
                from langchain.document_loaders import PyMuPDFLoader
                logger.info("Trying PyMuPDFLoader as fallback")
                loader = PyMuPDFLoader(tmp_file_path)
                documents = loader.load()
                logger.info(f"PDF loaded with PyMuPDFLoader: {len(documents)} pages")
            except Exception as fallback_error:
                logger.error(f"PyMuPDFLoader also failed: {str(fallback_error)}")
                raise HTTPException(status_code=400, detail=f"Could not read PDF file. Please ensure it's a valid PDF with readable text. Error: {str(pdf_error)}")
        
        # Validate that we have documents with content
        if not documents:
            raise HTTPException(status_code=400, detail="PDF appears to be empty or corrupted. Please try a different PDF file.")
        
        # Check if documents have actual content
        valid_documents = []
        for doc in documents:
            if doc.page_content and doc.page_content.strip():
                valid_documents.append(doc)
        
        if not valid_documents:
            raise HTTPException(status_code=400, detail="PDF contains no readable text. Please ensure the PDF has selectable text content.")
        
        documents = valid_documents
        logger.info(f"Valid documents after filtering: {len(documents)} pages")
        
        # Split documents into chunks
        logger.info("Splitting documents into chunks")
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )
        splits = text_splitter.split_documents(documents)
        logger.info(f"Documents split into {len(splits)} chunks")
        
        # Validate chunks have content
        valid_splits = []
        for split in splits:
            if split.page_content and split.page_content.strip():
                valid_splits.append(split)
        
        if not valid_splits:
            raise HTTPException(status_code=400, detail="PDF text could not be processed into meaningful chunks. Please try a different PDF.")
        
        splits = valid_splits
        logger.info(f"Valid chunks after filtering: {len(splits)} chunks")
        
        # Create embeddings and vector store
        logger.info("Creating embeddings and vector store")
        try:
            embeddings = HuggingFaceEmbeddings(
                model_name="sentence-transformers/all-MiniLM-L6-v2"
            )
            
            # Test embeddings generation with a small sample first
            test_text = splits[0].page_content[:100] if splits else "test"
            test_embedding = embeddings.embed_query(test_text)
            
            if not test_embedding or len(test_embedding) == 0:
                raise HTTPException(status_code=500, detail="Failed to generate embeddings. Please try again.")
            
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
                    # Create a more conversational prompt template
                    from langchain.prompts import PromptTemplate
                    
                    # Enhanced prompt for more friendly, conversational responses
                    prompt_template = """You are a helpful and friendly AI assistant who loves to help users understand their PDF documents. 
                    You should respond in a conversational, warm, and engaging manner - like talking to a friend who's genuinely interested in helping.
                    
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
    global qa_chain, vector_store, conversation_history
    
    logger.info(f"Received chat message: {chat_message.message[:100]}...")
    
    if not vector_store:
        logger.error("No PDF uploaded yet")
        raise HTTPException(status_code=400, detail="No PDF uploaded yet. Please upload a PDF first.")
    
    try:
        # Add user message to conversation history
        conversation_history.append({"role": "user", "content": chat_message.message})
        
        if qa_chain:
            # Use Gemini if available
            logger.info("Using Gemini QA chain for response")
            try:
                # Get response with source documents
                result = qa_chain({"query": chat_message.message})
                response = result["result"]
                source_docs = result.get("source_documents", [])
                
                # Extract sources from documents
                sources = []
                for doc in source_docs:
                    page_num = doc.metadata.get('page', 'Unknown')
                    sources.append(f"Page {page_num}")
                
                logger.info("Gemini response generated successfully")
                
            except Exception as gemini_error:
                logger.error(f"Gemini API error: {str(gemini_error)}")
                # Fallback to similarity search if Gemini fails
                logger.info("Falling back to similarity search due to Gemini error")
                docs = vector_store.similarity_search(chat_message.message, k=3)
                if not docs:
                    response = "Hey there! 😊 I'm having a little trouble connecting to my AI brain right now. Could you try asking your question again? Sometimes a fresh start helps!"
                    sources = []
                else:
                    response = "Based on what I found in your PDF:\n\n" + "\n\n".join([doc.page_content for doc in docs])
                    sources = [f"Page {doc.metadata.get('page', 'Unknown')}" for doc in docs]
        else:
            # Fallback to vector similarity search
            logger.info("Using similarity search fallback")
            docs = vector_store.similarity_search(chat_message.message, k=3)
            logger.info(f"Found {len(docs)} relevant documents")
            
            if not docs:
                response = "Hmm, I couldn't find anything directly related to that in your PDF. 🤔 Maybe try asking about a different aspect of the document, or rephrase your question? I'm here to help!"
                sources = []
            else:
                response = "Here's what I found in your PDF that might help:\n\n" + "\n\n".join([doc.page_content for doc in docs])
                sources = [f"Page {doc.metadata.get('page', 'Unknown')}" for doc in docs]
            
            logger.info("Similarity search response generated")
        
        # Add AI response to conversation history
        conversation_history.append({"role": "assistant", "content": response})
        
        # Keep only last 10 exchanges to manage memory
        if len(conversation_history) > 20:  # 10 user + 10 assistant messages
            conversation_history = conversation_history[-20:]
        
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

@app.get("/pdf-text")
async def get_pdf_text():
    """Get the extracted text from the uploaded PDF"""
    global documents
    
    if not documents:
        return {"message": "No PDF uploaded", "text": "", "status": "no_pdf"}
    
    try:
        # Combine all document text, filtering out empty content
        valid_texts = []
        for doc in documents:
            if doc.page_content and doc.page_content.strip():
                valid_texts.append(doc.page_content.strip())
        
        if not valid_texts:
            return {"message": "No readable text found in PDF", "text": "", "status": "no_text"}
        
        full_text = "\n\n".join(valid_texts)
        
        return {
            "text": full_text,
            "pages": len(documents),
            "valid_pages": len(valid_texts),
            "status": "success"
        }
    except Exception as e:
        logger.error(f"Error extracting PDF text: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error extracting PDF text: {str(e)}")

@app.post("/save-annotation")
async def save_annotation(annotation_data: dict):
    """Save whiteboard annotations"""
    # In a real application, you'd save this to a database
    # For now, we'll just return success
    return {"message": "Annotation saved successfully", "data": annotation_data}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
