import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv(override=True)

class Config:
    """Application configuration"""
    
    # Flask settings
    SECRET_KEY = os.urandom(24)
    DEBUG = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    HOST = os.getenv('FLASK_HOST', '0.0.0.0')
    PORT = int(os.getenv('FLASK_PORT', '5001'))
    
    # API Keys
    GROQ_API_KEY = os.getenv('GROQ_API_KEY')
    
    # RAG Configuration
    PDF_FOLDER = os.getenv('PDF_FOLDER', 'content/')
    CHROMA_PERSIST_DIR = os.getenv('CHROMA_PERSIST_DIR', 'dbVector')
    HF_EMBEDDING_MODEL_NAME = os.getenv('HF_EMBEDDING_MODEL', 'sentence-transformers/paraphrase-multilingual-mpnet-base-v2')
    GROQ_MODEL_NAME = os.getenv('GROQ_MODEL', 'llama3-8b-8192')
    
    # Processing settings
    DEFAULT_K_RETRIEVAL = int(os.getenv('DEFAULT_K_RETRIEVAL', '5'))
    CHUNK_SIZE = int(os.getenv('CHUNK_SIZE', '1000'))
    CHUNK_OVERLAP = int(os.getenv('CHUNK_OVERLAP', '200'))
    
    # Performance settings
    MAX_REBUILD_ATTEMPTS = 3
    RETRY_DELAY = 0.5
    
    @classmethod
    def validate(cls) -> Optional[str]:
        """Validate critical configuration values"""
        if not cls.GROQ_API_KEY:
            return "GROQ_API_KEY environment variable is required"
        
        if not os.path.exists(cls.PDF_FOLDER):
            try:
                os.makedirs(cls.PDF_FOLDER, exist_ok=True)
            except Exception as e:
                return f"Cannot create PDF folder: {e}"
        
        return None 