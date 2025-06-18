from typing import List, Optional, Dict, Any
from dataclasses import dataclass
from enum import Enum

class ChatMode(Enum):
    """Available chat modes"""
    RAG = "RAG"
    LLM_ONLY = "LLM_ONLY" 
    UNAVAILABLE = "UNAVAILABLE"

@dataclass
class ChatMessage:
    """Represents a chat message"""
    message: str
    timestamp: Optional[str] = None

@dataclass
class DocumentSource:
    """Represents a document source with metadata"""
    source_file: str
    page: str
    score: float

@dataclass
class ChatRequest:
    """Chat API request model"""
    message: str
    k_context: Optional[int] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ChatRequest':
        """Create ChatRequest from dictionary"""
        message = data.get('message', '').strip()
        if not message:
            raise ValueError("Message cannot be empty")
        
        k_context = data.get('k_context')
        if k_context is not None:
            try:
                k_context = int(k_context)
                if k_context <= 0:
                    raise ValueError("k_context must be positive")
            except (ValueError, TypeError):
                raise ValueError("k_context must be a positive integer")
        
        return cls(message=message, k_context=k_context)

@dataclass
class ChatResponse:
    """Chat API response model"""
    question: str
    response: str  # Changed from 'answer' to 'response' to match frontend expectation
    context_provided_to_llm: str
    sources: List[DocumentSource]
    mode: ChatMode
    error: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON response"""
        return {
            'question': self.question,
            'response': self.response,
            'context_provided_to_llm': self.context_provided_to_llm,
            'sources': [
                {
                    'source_file': src.source_file,
                    'page': src.page,
                    'score': src.score
                }
                for src in self.sources
            ],
            'mode': self.mode.value,
            'error': self.error
        }

@dataclass
class SystemStatus:
    """System status model"""
    rag_pipeline_ready: bool
    llm_ready: bool
    db_ready: bool
    loaded_documents: List[str]
    initialization_error: Optional[str]
    message: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON response"""
        return {
            'rag_pipeline_ready': self.rag_pipeline_ready,
            'llm_ready': self.llm_ready,
            'db_ready': self.db_ready,
            'loaded_pdfs': self.loaded_documents,  # Keep 'loaded_pdfs' for backward compatibility
            'initialization_error': self.initialization_error,
            'message': self.message
        } 