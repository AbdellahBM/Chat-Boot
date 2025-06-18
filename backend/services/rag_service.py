import os
import gc
import time
import shutil
import logging
from typing import List, Tuple, Optional

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_groq import ChatGroq
from langchain.schema import Document

from config import Config
from models.chat_models import DocumentSource, ChatMode
from utils.text_processing import validate_input

logger = logging.getLogger(__name__)

class RAGService:
    """Service for RAG operations"""
    
    def __init__(self):
        self.embedding_model: Optional[HuggingFaceEmbeddings] = None
        self.vector_db: Optional[Chroma] = None
        self.llm: Optional[ChatGroq] = None
        self.is_ready = False
        
    def initialize_embedding_model(self) -> Tuple[bool, Optional[str]]:
        """Initialize the embedding model"""
        try:
            logger.info(f"Initializing embedding model: {Config.HF_EMBEDDING_MODEL_NAME}")
            
            self.embedding_model = HuggingFaceEmbeddings(
                model_name=Config.HF_EMBEDDING_MODEL_NAME,
                model_kwargs={'device': 'cpu'}
            )
            
            # Test the model
            _ = self.embedding_model.embed_query("Test embedding")
            
            logger.info("Embedding model initialized successfully")
            return True, None
            
        except Exception as e:
            logger.error(f"Error initializing embedding model: {e}")
            self.embedding_model = None
            return False, f"Embedding model initialization failed: {str(e)}"
    
    def initialize_llm(self) -> Tuple[bool, Optional[str]]:
        """Initialize the LLM"""
        try:
            if not Config.GROQ_API_KEY:
                return False, "GROQ_API_KEY not configured"
            
            logger.info(f"Initializing LLM: {Config.GROQ_MODEL_NAME}")
            
            self.llm = ChatGroq(
                model_name=Config.GROQ_MODEL_NAME,
                api_key=Config.GROQ_API_KEY,
                temperature=0.1
            )
            
            # Test the LLM
            _ = self.llm.invoke("Hello")
            
            logger.info("LLM initialized successfully")
            return True, None
            
        except Exception as e:
            logger.error(f"Error initializing LLM: {e}")
            self.llm = None
            return False, f"LLM initialization failed: {str(e)}"
    
    def initialize_vector_store(self, chunks: List[Document]) -> Tuple[bool, Optional[str]]:
        """Initialize or load the vector store"""
        try:
            if not self.embedding_model:
                return False, "Embedding model not initialized"
            
            if not chunks:
                return False, "No chunks provided for vector store"
            
            logger.info("Initializing vector store")
            
            # Create persist directory
            os.makedirs(Config.CHROMA_PERSIST_DIR, exist_ok=True)
            
            # Check if we need to rebuild
            needs_rebuild = self._check_vector_store_rebuild(chunks)
            
            if needs_rebuild:
                success = self._rebuild_vector_store(chunks)
                if not success:
                    return False, "Failed to rebuild vector store"
            else:
                logger.info("Using existing vector store")
            
            logger.info("Vector store initialized successfully")
            return True, None
            
        except Exception as e:
            logger.error(f"Error initializing vector store: {e}")
            self.vector_db = None
            return False, f"Vector store initialization failed: {str(e)}"
    
    def _check_vector_store_rebuild(self, chunks: List[Document]) -> bool:
        """Check if vector store needs to be rebuilt"""
        try:
            if not os.path.exists(Config.CHROMA_PERSIST_DIR):
                return True
            
            if not any(os.scandir(Config.CHROMA_PERSIST_DIR)):
                return True
            
            # Try to load existing store
            temp_db = Chroma(
                persist_directory=Config.CHROMA_PERSIST_DIR,
                embedding_function=self.embedding_model
            )
            
            existing_count = temp_db._collection.count()
            current_count = len(chunks)
            
            if existing_count != current_count:
                logger.info(f"Vector store count mismatch: {existing_count} vs {current_count}")
                return True
            
            # Store for use if no rebuild needed
            self.vector_db = temp_db
            return False
            
        except Exception as e:
            logger.warning(f"Error checking vector store: {e}")
            return True
    
    def _rebuild_vector_store(self, chunks: List[Document]) -> bool:
        """Rebuild the vector store from chunks"""
        try:
            logger.info("Rebuilding vector store")
            
            # Clean up existing instance
            if self.vector_db:
                del self.vector_db
                self.vector_db = None
                gc.collect()
            
            # Remove existing data
            self._clean_vector_store_directory()
            
            # Create new store
            self.vector_db = Chroma.from_documents(
                documents=chunks,
                embedding=self.embedding_model,
                persist_directory=Config.CHROMA_PERSIST_DIR
            )
            
            logger.info(f"Vector store rebuilt with {len(chunks)} chunks")
            return True
            
        except Exception as e:
            logger.error(f"Error rebuilding vector store: {e}")
            return False
    
    def _clean_vector_store_directory(self):
        """Clean the vector store directory"""
        if not os.path.exists(Config.CHROMA_PERSIST_DIR):
            return
        
        for attempt in range(Config.MAX_REBUILD_ATTEMPTS):
            try:
                for item in os.listdir(Config.CHROMA_PERSIST_DIR):
                    item_path = os.path.join(Config.CHROMA_PERSIST_DIR, item)
                    if os.path.isdir(item_path):
                        shutil.rmtree(item_path)
                    else:
                        os.unlink(item_path)
                break
                
            except PermissionError as e:
                logger.warning(f"Attempt {attempt + 1} to clean directory failed: {e}")
                if attempt < Config.MAX_REBUILD_ATTEMPTS - 1:
                    time.sleep(Config.RETRY_DELAY)
                else:
                    logger.error("Failed to clean vector store directory")
                    
            except Exception as e:
                logger.error(f"Unexpected error cleaning directory: {e}")
                break
    
    def search_similar_documents(self, query: str, k: int = None) -> Tuple[str, List[DocumentSource]]:
        """Search for similar documents"""
        if not self.vector_db:
            logger.error("Vector database not initialized")
            return "", []
        
        if k is None:
            k = Config.DEFAULT_K_RETRIEVAL
        
        try:
            # Validate input
            is_valid, error_msg = validate_input(query)
            if not is_valid:
                logger.warning(f"Invalid search query: {error_msg}")
                return "", []
            
            logger.info(f"Searching for similar documents: query='{query[:50]}...', k={k}")
            
            similar_docs = self.vector_db.similarity_search_with_score(query, k=k)
            
            if not similar_docs:
                logger.info("No similar documents found")
                return "", []
            
            # Extract content and sources
            contents = []
            sources = []
            
            for doc, score in similar_docs:
                contents.append(doc.page_content)
                sources.append(DocumentSource(
                    source_file=doc.metadata.get('source_file', 'Unknown'),
                    page=str(doc.metadata.get('page', 'N/A')),
                    score=float(f"{score:.4f}")
                ))
            
            concatenated_content = "\n\n---\n\n".join(contents)
            
            logger.info(f"Found {len(similar_docs)} similar documents")
            return concatenated_content, sources
            
        except Exception as e:
            logger.error(f"Error searching similar documents: {e}")
            return "", []
    
    def generate_response(self, query: str, context: str = "") -> Tuple[str, ChatMode]:
        """Generate response using LLM"""
        if not self.llm:
            return "LLM not available", ChatMode.UNAVAILABLE
        
        try:
            # Validate input
            is_valid, error_msg = validate_input(query)
            if not is_valid:
                return f"Invalid input: {error_msg}", ChatMode.UNAVAILABLE
            
            if context:
                # RAG mode with context
                prompt = self._create_rag_prompt(query, context)
                mode = ChatMode.RAG
            else:
                # LLM only mode
                prompt = query
                mode = ChatMode.LLM_ONLY
            
            logger.info(f"Generating response with {mode.value} mode")
            
            response = self.llm.invoke(prompt)
            answer = response.content if hasattr(response, 'content') else str(response)
            
            return answer.strip(), mode
            
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return "Sorry, an error occurred while generating the response", ChatMode.UNAVAILABLE
    
    def _create_rag_prompt(self, query: str, context: str) -> str:
        """Create RAG prompt with instructions"""
        return f"""You are a helpful assistant with access to specific document context. Follow these guidelines:

1. **PRIMARY PRIORITY**: Use the information from the provided CONTEXT below to answer the question.
2. **SECONDARY PRIORITY**: If the context doesn't contain sufficient information, you may supplement with your general knowledge, but clearly indicate when you're doing so.
3. **TRANSPARENCY**: Always specify your sources:
   - For context-based info: "According to the provided documents..." or "Based on the context..."
   - For general knowledge: "Based on general knowledge..." or "Generally speaking..."
4. **ACCURACY**: Be factual and helpful. Don't make up specific details not found in either source.
5. **COMPLETENESS**: Provide comprehensive answers when possible.

CONTEXT FROM DOCUMENTS:
--- start of context ---
{context}
--- end of context ---

QUESTION:
{query}

HELPFUL RESPONSE (prioritizing context, supplementing with general knowledge when needed):"""
    
    def is_available(self) -> bool:
        """Check if RAG service is available"""
        return bool(self.llm)
    
    def is_rag_ready(self) -> bool:
        """Check if full RAG pipeline is ready"""
        return bool(self.llm and self.vector_db and self.embedding_model)
    
    def clear(self):
        """Clear all components"""
        if self.vector_db:
            del self.vector_db 
            self.vector_db = None
        
        if self.embedding_model:
            del self.embedding_model
            self.embedding_model = None
            
        if self.llm:
            del self.llm
            self.llm = None
            
        self.is_ready = False
        gc.collect() 