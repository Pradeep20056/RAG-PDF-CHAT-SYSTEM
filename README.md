# PDF RAG Chat System

A comprehensive web application that allows users to upload PDF documents, chat with AI about their content using RAG (Retrieval-Augmented Generation), and use a whiteboard to mark areas of doubt.

## Features

### 🚀 **PDF Upload & Processing**
- Drag-and-drop PDF upload interface
- Automatic PDF text extraction and chunking
- Vector embedding generation using sentence transformers
- Support for large PDF documents

### 💬 **Enhanced AI Chat Interface**
- **Gemini Integration**: Powered by Google's Gemini models for intelligent, conversational responses
- **Friendly AI Assistant**: Chat with a warm, helpful AI that responds like a friend
- **🎤 Voice Input**: Speak your questions using your microphone - just click and talk!
- **🔊 Voice Output**: AI responses are automatically spoken back to you
- **PDF Text Display**: View extracted PDF content in a scrollable text area for reference
- **Copy Functionality**: Copy AI responses and PDF text with one click
- **Conversation Memory**: AI remembers context from previous messages for better interactions
- **Source Attribution**: See exactly which pages your answers come from
- **Smart Fallback**: Automatic fallback to similarity search if Gemini is unavailable

### 🎨 **Interactive Whiteboard**
- Drawing tools (pen, shapes, text)
- Color palette and brush size controls
- Annotation saving and downloading
- Perfect for marking areas of confusion

### 📱 **Modern UI/UX**
- Responsive design with Tailwind CSS
- Tab-based navigation
- PDF viewer with zoom and navigation
- Clean, intuitive interface

## Technology Stack

### Backend
- **FastAPI** - Modern Python web framework
- **LangChain** - RAG and LLM orchestration
- **Google Gemini** - Advanced AI models for conversational responses
- **ChromaDB** - Vector database for embeddings
- **Sentence Transformers** - Text embedding generation
- **PyPDF2** - PDF text extraction

### Frontend
- **React** - Modern JavaScript framework
- **Tailwind CSS** - Utility-first CSS framework
- **Fabric.js** - Canvas drawing library
- **React-PDF** - PDF viewing component
- **Axios** - HTTP client

## Prerequisites

- Python 3.8+
- Node.js 16+
- npm or yarn
- **Modern Web Browser** with Web Speech API support:
  - Chrome/Chromium (recommended)
  - Edge
  - Safari (limited support)
  - Firefox (limited support)
- **Microphone access** for voice input
- **Audio output** for voice responses

## Installation

### 1. Clone the Repository
```bash
git clone <repository-url>
cd pdf-rag-chat-system
```

### 2. Backend Setup
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp env_example.txt .env

# Add your Gemini API key to .env file
# Get your API key from: https://makersuite.google.com/app/apikey
echo "GEMINI_API_KEY=your_actual_gemini_api_key_here" >> .env
# Edit .env file with your OpenAI API key (optional)
```

### 3. Frontend Setup
```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm start
```

### 4. Start Backend Server
```bash
# In a new terminal, from the root directory
cd backend
python main.py
```

The application will be available at:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000

## Testing the Integration

### Test Backend API
```bash
# Run the test script to verify Gemini integration
python test_gemini_integration.py
```

This will test:
- ✅ Health check endpoint
- ✅ PDF upload and processing
- ✅ PDF text extraction
- ✅ Chat functionality with Gemini
- ✅ Conversation memory and context

### Manual Testing
1. **Start Backend**: `cd backend && python main.py`
2. **Start Frontend**: `cd frontend && npm start`
3. **Upload PDF**: Drag and drop a PDF file
4. **Start Chatting**: Ask questions like:
   - "Hey, what's this document about?"
   - "Can you help me understand this concept?"
   - "What are the main takeaways?"
   - "I'm confused about this part, can you help?"

## Usage

### 1. Upload PDF
- Navigate to the Upload tab
- Drag and drop your PDF file or click to browse
- Wait for processing to complete

### 2. View PDF
- Use the PDF Viewer tab to browse your document
- Navigate between pages
- Zoom in/out for better readability

### 3. Chat with AI
- Go to the Chat tab
- **🎤 Voice Input**: Click the microphone icon to speak your questions
- **🔊 Voice Output**: AI responses are automatically spoken (toggle with volume icon)
- **View PDF Text**: Click "Show PDF Text" to see extracted content
- **Friendly Chat**: Ask questions in a conversational way:
  - "Hey, what's this document about?"
  - "Can you help me understand this concept?"
  - "I'm confused about this part, can you help?"
- **Copy Responses**: Click the copy icon to save AI responses
- **Replay Messages**: Click the speaker icon on any AI message to hear it again
- **Source References**: See which pages your answers come from
- **Conversation Memory**: AI remembers context from previous messages

### 4. Use Whiteboard
- Access the Whiteboard tab
- Use drawing tools to mark areas of doubt
- Add text annotations
- Download your annotations as images

## Configuration

### Environment Variables
Create a `.env` file in the root directory:

```env
# OpenAI API Key (optional - for enhanced responses)
OPENAI_API_KEY=your_openai_api_key_here

# Server Configuration
HOST=0.0.0.0
PORT=8000

# CORS Origins
FRONTEND_URL=http://localhost:3000
```

### OpenAI Integration (Optional)
- Get an API key from [OpenAI](https://platform.openai.com/)
- Add it to your `.env` file
- The system will use GPT for enhanced responses
- Without it, falls back to vector similarity search

## API Endpoints

### Backend API
- `POST /upload-pdf` - Upload and process PDF
- `POST /chat` - Send chat message
- `GET /pdf-info` - Get PDF information
- `POST /save-annotation` - Save whiteboard annotations

## Project Structure

```
pdf-rag-chat-system/
├── backend/
│   └── main.py              # FastAPI server
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── components/      # React components
│   │   ├── App.js           # Main app component
│   │   └── index.js         # Entry point
│   ├── package.json
│   └── tailwind.config.js
├── requirements.txt          # Python dependencies
├── env_example.txt          # Environment variables template
└── README.md
```

## Features in Detail

### RAG Implementation
- **Document Loading**: PDF text extraction using PyPDF2
- **Text Chunking**: Recursive character splitting for optimal retrieval
- **Embedding Generation**: Sentence transformers for vector representation
- **Vector Storage**: ChromaDB for efficient similarity search
- **Retrieval**: Top-k document retrieval based on query similarity

### Whiteboard Capabilities
- **Drawing Tools**: Freehand pen, rectangles, circles
- **Text Annotations**: Click-to-add text with custom styling
- **Object Manipulation**: Select, move, resize, delete objects
- **Export**: Download annotations as PNG images

### PDF Processing
- **Multi-page Support**: Handle documents of any length
- **Text Extraction**: Clean text extraction for analysis
- **Chunking Strategy**: Overlapping chunks for context preservation
- **Progress Tracking**: Real-time upload progress indication

## Troubleshooting

### Common Issues

1. **PDF Upload Fails**
   - Ensure file is a valid PDF
   - Check file size (recommended < 10MB)
   - Verify backend server is running

2. **Chat Not Working**
   - Check if PDF was uploaded successfully
   - Verify backend API connectivity
   - Check browser console for errors

3. **Whiteboard Not Loading**
   - Ensure Fabric.js is properly loaded
   - Check browser compatibility
   - Clear browser cache if needed

### Performance Tips

- Use smaller PDFs for faster processing
- Close unnecessary browser tabs
- Ensure stable internet connection for API calls

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions:
- Create an issue in the repository
- Check the troubleshooting section
- Review the API documentation

## Future Enhancements

- [ ] User authentication and document management
- [ ] Multiple document support
- [ ] Advanced annotation tools
- [ ] Export to various formats
- [ ] Mobile app version
- [ ] Collaborative whiteboarding
- [ ] Integration with cloud storage
- [ ] Advanced RAG techniques (hybrid search, re-ranking)
