import re
from typing import List, Any

def normalize_text(text: str) -> str:
    """
    Clean text by normalizing spaces and removing artifacts.
    
    Args:
        text: Raw text to normalize
        
    Returns:
        Cleaned text string
    """
    if not isinstance(text, str):
        return ""
    
    # Remove excessive whitespace and normalize
    text = re.sub(r'\s+', ' ', text).strip()
    
    # Remove hyphenated line breaks
    text = re.sub(r'-\n', '', text)
    
    # Remove other common PDF artifacts
    text = re.sub(r'\n+', '\n', text)  # Multiple newlines to single
    text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]', '', text)  # Control chars
    
    return text

def validate_input(text: str, max_length: int = 5000) -> tuple[bool, str]:
    """
    Validate user input for safety and length.
    
    Args:
        text: Text to validate
        max_length: Maximum allowed length
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not isinstance(text, str):
        return False, "Input must be a string"
    
    text = text.strip()
    
    if not text:
        return False, "Input cannot be empty"
    
    if len(text) > max_length:
        return False, f"Input too long (max {max_length} characters)"
    
    # Check for potential injection patterns
    suspicious_patterns = [
        r'<script.*?>.*?</script>',
        r'javascript:',
        r'on\w+\s*=',
        r'data:text/html',
    ]
    
    for pattern in suspicious_patterns:
        if re.search(pattern, text, re.IGNORECASE):
            return False, "Input contains suspicious content"
    
    return True, ""

def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename for safe storage.
    
    Args:
        filename: Original filename
        
    Returns:
        Sanitized filename
    """
    if not isinstance(filename, str):
        return "unknown_file"
    
    # Remove path traversal attempts
    filename = filename.replace('..', '').replace('/', '').replace('\\', '')
    
    # Keep only alphanumeric, dots, hyphens, and underscores
    filename = re.sub(r'[^a-zA-Z0-9._-]', '_', filename)
    
    # Ensure it's not empty
    if not filename:
        return "unknown_file"
    
    return filename

def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
    """
    Simple text chunking utility.
    
    Args:
        text: Text to chunk
        chunk_size: Size of each chunk
        overlap: Overlap between chunks
        
    Returns:
        List of text chunks
    """
    if not text or chunk_size <= 0:
        return []
    
    chunks = []
    start = 0
    
    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunk = text[start:end]
        
        if chunk.strip():
            chunks.append(chunk)
        
        start = end - overlap if overlap > 0 else end
        
        # Prevent infinite loop
        if start >= end:
            break
    
    return chunks 