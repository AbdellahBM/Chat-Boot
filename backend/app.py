import logging
import sys
from flask import Flask, request, jsonify
from flask_cors import CORS

from config import Config
from models.chat_models import ChatRequest, ChatResponse, SystemStatus, ChatMode
from services.document_service import DocumentService
from services.rag_service import RAGService
from utils.text_processing import validate_input

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('chatbot.log')
    ]
)

logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app)
app.secret_key = Config.SECRET_KEY

# Global services
document_service: DocumentService = None
rag_service: RAGService = None
system_ready = False
initialization_error = None

def initialize_system():
    """Initialize the complete system"""
    global document_service, rag_service, system_ready, initialization_error
    
    logger.info("=== Starting system initialization ===")
    
    # Validate configuration
    config_error = Config.validate()
    if config_error:
        initialization_error = config_error
        logger.error(f"Configuration validation failed: {config_error}")
        return False
    
    try:
        # Initialize services
        document_service = DocumentService()
        rag_service = RAGService()
        
        # Initialize LLM first (most critical)
        llm_success, llm_error = rag_service.initialize_llm()
        if not llm_success:
            initialization_error = f"LLM initialization failed: {llm_error}"
            logger.error(initialization_error)
            return False
        
        # Load documents
        doc_success, doc_error = document_service.load_documents()
        if not doc_success:
            logger.warning(f"Document loading failed: {doc_error}")
            # Continue without documents (LLM-only mode)
            system_ready = True
            return True
        
        # Create chunks
        chunk_success, chunk_error = document_service.create_chunks()
        if not chunk_success:
            logger.warning(f"Chunk creation failed: {chunk_error}")
            system_ready = True
            return True
        
        # Initialize embedding model
        embed_success, embed_error = rag_service.initialize_embedding_model()
        if not embed_success:
            logger.warning(f"Embedding model failed: {embed_error}")
            system_ready = True
            return True
        
        # Initialize vector store
        vector_success, vector_error = rag_service.initialize_vector_store(
            document_service.get_chunks()
        )
        if not vector_success:
            logger.warning(f"Vector store failed: {vector_error}")
            system_ready = True
            return True
        
        system_ready = True
        
        if rag_service.is_rag_ready():
            logger.info("✅ === System fully initialized (RAG mode) ===")
        else:
            logger.info("✅ === System initialized (LLM-only mode) ===")
        
        return True
        
    except Exception as e:
        initialization_error = f"System initialization failed: {str(e)}"
        logger.error(f"Critical error during initialization: {e}", exc_info=True)
        return False

@app.route('/api/status', methods=['GET'])
def api_status():
    """Get system status"""
    try:
        if not system_ready or not rag_service:
            status = SystemStatus(
                rag_pipeline_ready=False,
                llm_ready=False,
                db_ready=False,
                loaded_documents=[],
                initialization_error=initialization_error or "System not initialized",
                message="System not ready"
            )
        else:
            loaded_docs = document_service.get_loaded_filenames() if document_service else []
            
            if rag_service.is_rag_ready():
                message = "System ready (RAG mode with documents)"
            elif rag_service.is_available():
                message = "System ready (LLM-only mode)"
            else:
                message = "System has issues"
            
            status = SystemStatus(
                rag_pipeline_ready=rag_service.is_rag_ready(),
                llm_ready=rag_service.is_available(),
                db_ready=rag_service.is_rag_ready(),
                loaded_documents=loaded_docs,
                initialization_error=initialization_error,
                message=message
            )
        
        return jsonify(status.to_dict())
        
    except Exception as e:
        logger.error(f"Error in status endpoint: {e}")
        return jsonify({"error": "Status check failed"}), 500

@app.route('/api/chat', methods=['POST'])
def api_chat():
    """Handle chat requests"""
    try:
        # Validate request
        if not request.is_json:
            return jsonify({"error": "Request must be JSON"}), 400
        
        # Check system readiness
        if not system_ready or not rag_service or not rag_service.is_available():
            error_msg = initialization_error or "System not ready"
            return jsonify({
                "error": "System unavailable",
                "details": error_msg
            }), 503
        
        # Parse request
        try:
            chat_request = ChatRequest.from_dict(request.get_json())
        except ValueError as e:
            return jsonify({"error": str(e)}), 400
        
        logger.info(f"Processing chat request: '{chat_request.message[:50]}...'")
        
        # Determine processing mode
        k_context = chat_request.k_context or Config.DEFAULT_K_RETRIEVAL
        
        if rag_service.is_rag_ready():
            # RAG mode
            context, sources = rag_service.search_similar_documents(
                chat_request.message, k_context
            )
            
            if context:
                response_text, mode = rag_service.generate_response(
                    chat_request.message, context
                )
                context_info = f"Used {len(sources)} document sources"
            else:
                # Fallback to LLM-only if no context found
                response_text, mode = rag_service.generate_response(
                    chat_request.message
                )
                sources = []
                context_info = "No relevant documents found, using LLM-only mode"
        else:
            # LLM-only mode
            response_text, mode = rag_service.generate_response(chat_request.message)
            sources = []
            context_info = "LLM-only mode (no documents available)"
        
        # Create response
        chat_response = ChatResponse(
            question=chat_request.message,
            response=response_text,
            context_provided_to_llm=context_info,
            sources=sources,
            mode=mode
        )
        
        logger.info(f"Response generated in {mode.value} mode")
        return jsonify(chat_response.to_dict())
        
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}", exc_info=True)
        return jsonify({
            "error": "Chat processing failed",
            "details": "Internal server error"
        }), 500

@app.route('/api/reinitialize', methods=['POST'])
def api_reinitialize():
    """Reinitialize the system"""
    try:
        logger.info("Reinitializing system...")
        
        # Clear existing services
        global document_service, rag_service, system_ready, initialization_error
        
        if document_service:
            document_service.clear()
        
        if rag_service:
            rag_service.clear()
        
        system_ready = False
        initialization_error = None
        
        # Reinitialize
        success = initialize_system()
        
        if success:
            logger.info("Reinitialization completed successfully")
        else:
            logger.error("Reinitialization failed")
        
        return api_status()
        
    except Exception as e:
        logger.error(f"Error during reinitialization: {e}", exc_info=True)
        return jsonify({
            "error": "Reinitialization failed",
            "details": str(e)
        }), 500

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({"error": "Endpoint not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    logger.error(f"Internal server error: {error}")
    return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    logger.info("Starting Chatbot Application")
    
    # Initialize system
    if initialize_system():
        logger.info(f"Starting Flask server on {Config.HOST}:{Config.PORT}")
        app.run(
            debug=Config.DEBUG,
            host=Config.HOST,
            port=Config.PORT
        )
    else:
        logger.error("Failed to initialize system. Exiting.")
        sys.exit(1) 