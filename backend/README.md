# Chatbot Backend - Flask API Server

This is the backend API server for the AI-powered chatbot, built with Flask and implementing RAG (Retrieval-Augmented Generation) using LangChain, ChromaDB, and Groq LLM.

## 🤖 Features

- **RAG Implementation**: Advanced document retrieval and AI response generation
- **Vector Database**: ChromaDB for efficient document storage and similarity search
- **Multi-format Support**: PDF and CSV document processing
- **Groq LLM Integration**: Fast and powerful language model responses
- **CORS Enabled**: Cross-origin requests support for frontend integration
- **Multilingual**: Supports multiple languages with specialized embeddings
- **Document Chunking**: Intelligent text splitting for optimal retrieval

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- pip package manager
- Virtual environment (recommended)

### Installation

```bash
# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start the server
python app.py
```

The API server will be available at `http://localhost:5001`

## 📋 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/chat` | POST | Send message and get AI response |
| `/health` | GET | Server health check |

### Chat API Example

```bash
curl -X POST http://localhost:5001/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello, I need help with gifts"}'
```

Response:
```json
{
  "response": "I'd be happy to help you find the perfect gift! What type of gift are you looking for?",
  "status": "success"
}
```

## 🏗️ Architecture

```
backend/
├── app.py                 # Main Flask application
├── config.py             # Configuration settings
├── requirements.txt      # Python dependencies
├── content/              # Document storage
├── services/             # Business logic
│   ├── document_service.py
│   ├── rag_service.py
│   └── ...
├── models/               # Data models
├── utils/                # Utility functions
└── rag/                  # RAG implementation
```

## 🔧 Configuration

### Environment Variables
Create a `.env` file in the backend directory:

```env
GROQ_API_KEY=your_groq_api_key_here
FLASK_ENV=development
FLASK_DEBUG=True
```

### Document Configuration
- Place PDF files in the `content/` directory
- CSV files are automatically processed
- Vector database is created in `dbVector/` (auto-generated)

## 🧠 RAG System

### Document Processing
1. **PDF Extraction**: Uses PyPDF2 for text extraction
2. **CSV Processing**: Pandas for structured data handling
3. **Text Chunking**: LangChain for intelligent text splitting
4. **Embeddings**: Sentence-transformers for multilingual support

### Vector Search
- **ChromaDB**: High-performance vector database
- **Similarity Search**: Cosine similarity for document retrieval
- **Top-K Retrieval**: Configurable number of relevant documents

### LLM Integration
- **Groq API**: Fast inference with Llama3-8B model
- **Context Injection**: Retrieved documents enhance responses
- **Fallback Mode**: Direct LLM responses when no relevant docs found

## 📊 Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| flask | 3.0.0 | Web framework |
| flask-cors | 4.0.0 | CORS support |
| groq | 0.4.0 | LLM API client |
| langchain | 0.1.0 | RAG framework |
| chromadb | 0.4.22 | Vector database |
| sentence-transformers | 2.2.2 | Text embeddings |
| PyPDF2 | 3.0.1 | PDF processing |
| pandas | 2.1.4 | Data manipulation |

## 🔄 Data Flow

1. **Document Ingestion**: Load PDFs/CSVs → Extract text → Create chunks
2. **Vectorization**: Generate embeddings → Store in ChromaDB
3. **Query Processing**: User message → Similarity search → Retrieve context
4. **Response Generation**: Context + Query → Groq LLM → Return response

## 🛠️ Development

### Adding New Document Sources
1. Place documents in the `content/` directory
2. Restart the server to trigger re-indexing
3. The system will automatically process new files

### Customizing the RAG Pipeline
- Modify chunk size in `services/document_service.py`
- Adjust similarity threshold in `services/rag_service.py`
- Change embedding model in configuration

### Logging
The application logs activities to `chatbot.log` (auto-generated):
- Document processing status
- Query processing times
- Error tracking

## 🐛 Troubleshooting

**Vector database errors:**
```bash
rm -rf dbVector/  # Remove and restart to rebuild
```

**Missing API key:**
- Set GROQ_API_KEY in environment variables
- Check `.env` file configuration

**Document processing fails:**
- Verify PDF files are not corrupted
- Check file permissions in `content/` directory

**Port 5001 already in use:**
```bash
# Modify port in app.py
app.run(host='0.0.0.0', port=5002)
```

## 🚀 Production Deployment

For production deployment:

1. **Use WSGI Server**:
   ```bash
   pip install gunicorn
   gunicorn -w 4 -b 0.0.0.0:5001 app:app
   ```

2. **Environment Configuration**:
   - Set `FLASK_ENV=production`
   - Configure proper API keys
   - Set up reverse proxy (nginx)

3. **Performance Optimization**:
   - Pre-build vector database
   - Use production-grade ChromaDB setup
   - Configure proper logging levels

## 📈 Performance

- **Response Time**: ~500-2000ms depending on document corpus size
- **Concurrent Users**: Supports multiple simultaneous requests
- **Memory Usage**: ~2-4GB depending on document collection
- **Scalability**: Horizontal scaling supported with external vector DB

---

**Note:** This backend requires a valid Groq API key to function. The vector database will be automatically created on first run. 