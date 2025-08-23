# PDF RAG Chat System

A comprehensive web application that allows users to upload PDF documents, chat with AI about their content using RAG (Retrieval-Augmented Generation), and use a whiteboard to mark areas of doubt.

## Features

### 🚀 **PDF Upload & Processing**
- Drag-and-drop PDF upload interface
- Automatic PDF text extraction and chunking
- Vector embedding generation using sentence transformers
- Support for large PDF documents

### 💬 **AI Chat Interface**
- RAG-powered question answering about PDF content
- Real-time chat with AI assistant
- Source attribution for answers
- Fallback to vector similarity search when OpenAI is unavailable

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
- Ask questions about your PDF content
- Get AI-powered answers with source references

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
