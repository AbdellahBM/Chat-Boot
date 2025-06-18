import os
import logging
from typing import List, Tuple, Optional
from langchain_community.document_loaders import PyPDFLoader, CSVLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document

from config import Config
from utils.text_processing import normalize_text, sanitize_filename

logger = logging.getLogger(__name__)

class DocumentService:
    """Service for handling document operations"""
    
    def __init__(self):
        self.loaded_documents: List[Document] = []
        self.chunks: List[Document] = []
        self.loaded_filenames: List[str] = []
        
    def load_documents(self) -> Tuple[bool, Optional[str]]:
        """
        Load all documents from the configured folder.
        
        Returns:
            Tuple of (success, error_message)
        """
        try:
            self.loaded_documents.clear()
            self.loaded_filenames.clear()
            
            # Create folder if it doesn't exist
            os.makedirs(Config.PDF_FOLDER, exist_ok=True)
            
            # Load PDFs
            pdf_success = self._load_pdf_files()
            
            # Load CSVs  
            csv_success = self._load_csv_files()
            
            if not self.loaded_documents:
                return False, "No valid documents found to load"
            
            logger.info(f"Successfully loaded {len(self.loaded_documents)} pages from {len(self.loaded_filenames)} files")
            return True, None
            
        except Exception as e:
            logger.error(f"Error loading documents: {e}")
            return False, f"Document loading failed: {str(e)}"
    
    def _load_pdf_files(self) -> bool:
        """Load PDF files from the content folder"""
        try:
            pdf_files = [f for f in os.listdir(Config.PDF_FOLDER) if f.lower().endswith('.pdf')]
            
            if not pdf_files:
                logger.info("No PDF files found")
                return True
            
            logger.info(f"Found {len(pdf_files)} PDF files to process")
            
            for pdf_file in pdf_files:
                self._load_single_pdf(pdf_file)
                
            return True
            
        except Exception as e:
            logger.error(f"Error loading PDF files: {e}")
            return False
    
    def _load_single_pdf(self, filename: str) -> bool:
        """Load a single PDF file"""
        try:
            safe_filename = sanitize_filename(filename)
            file_path = os.path.join(Config.PDF_FOLDER, filename)
            
            if not os.path.exists(file_path):
                logger.warning(f"PDF file not found: {filename}")
                return False
            
            logger.info(f"Loading PDF: {filename}")
            
            loader = PyPDFLoader(file_path)
            pages = loader.load()
            
            if not pages:
                logger.warning(f"No pages extracted from {filename}")
                return False
            
            valid_pages = []
            for page in pages:
                page.page_content = normalize_text(page.page_content)
                
                if not page.page_content.strip():
                    continue
                
                page.metadata["source_file"] = safe_filename
                valid_pages.append(page)
            
            if valid_pages:
                self.loaded_documents.extend(valid_pages)
                if safe_filename not in self.loaded_filenames:
                    self.loaded_filenames.append(safe_filename)
                logger.info(f"Loaded {len(valid_pages)} valid pages from {filename}")
                return True
            else:
                logger.warning(f"No valid content found in {filename}")
                return False
                
        except Exception as e:
            logger.error(f"Error loading PDF {filename}: {e}")
            return False
    
    def _load_csv_files(self) -> bool:
        """Load CSV files from the content folder"""
        try:
            csv_files = [f for f in os.listdir(Config.PDF_FOLDER) if f.lower().endswith('.csv')]
            
            if not csv_files:
                logger.info("No CSV files found")
                return True
            
            logger.info(f"Found {len(csv_files)} CSV files to process")
            
            for csv_file in csv_files:
                self._load_single_csv(csv_file)
                
            return True
            
        except Exception as e:
            logger.error(f"Error loading CSV files: {e}")
            return False
    
    def _load_single_csv(self, filename: str) -> bool:
        """Load a single CSV file"""
        try:
            safe_filename = sanitize_filename(filename)
            file_path = os.path.join(Config.PDF_FOLDER, filename)
            
            if not os.path.exists(file_path):
                logger.warning(f"CSV file not found: {filename}")
                return False
            
            logger.info(f"Loading CSV: {filename}")
            
            loader = CSVLoader(file_path=file_path)
            csv_docs = loader.load()
            
            if not csv_docs:
                logger.warning(f"No content loaded from {filename}")
                return False
            
            for doc in csv_docs:
                doc.metadata["source_file"] = safe_filename
            
            self.loaded_documents.extend(csv_docs)
            if safe_filename not in self.loaded_filenames:
                self.loaded_filenames.append(safe_filename)
                
            logger.info(f"Loaded {len(csv_docs)} rows from {filename}")
            return True
            
        except Exception as e:
            logger.error(f"Error loading CSV {filename}: {e}")
            return False
    
    def create_chunks(self) -> Tuple[bool, Optional[str]]:
        """
        Split loaded documents into chunks.
        
        Returns:
            Tuple of (success, error_message)
        """
        try:
            if not self.loaded_documents:
                return False, "No documents loaded to chunk"
            
            logger.info(f"Creating chunks from {len(self.loaded_documents)} documents")
            
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=Config.CHUNK_SIZE,
                chunk_overlap=Config.CHUNK_OVERLAP,
                length_function=len,
                add_start_index=True
            )
            
            self.chunks = text_splitter.split_documents(self.loaded_documents)
            
            if not self.chunks:
                return False, "No chunks created from documents"
            
            logger.info(f"Created {len(self.chunks)} chunks")
            return True, None
            
        except Exception as e:
            logger.error(f"Error creating chunks: {e}")
            return False, f"Chunk creation failed: {str(e)}"
    
    def get_documents(self) -> List[Document]:
        """Get loaded documents"""
        return self.loaded_documents.copy()
    
    def get_chunks(self) -> List[Document]:
        """Get document chunks"""
        return self.chunks.copy()
    
    def get_loaded_filenames(self) -> List[str]:
        """Get list of loaded filenames"""
        return self.loaded_filenames.copy()
    
    def clear(self):
        """Clear all loaded data"""
        self.loaded_documents.clear()
        self.chunks.clear()
        self.loaded_filenames.clear() 