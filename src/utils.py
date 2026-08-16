import uuid
import re
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Union, Tuple, Any

logger = logging.getLogger(__name__)

def generate_id() -> str:
    """Generate a UUID-based short ID."""
    return str(uuid.uuid4())[:8]

def clean_text(text: str) -> str:
    """Normalize whitespace and strip text."""
    if not text:
        return ""
    # Replace multiple whitespaces/newlines with a single space
    cleaned = re.sub(r'\s+', ' ', text)
    return cleaned.strip()

def format_date(dt: datetime) -> str:
    """Format datetime to string."""
    if not dt:
        return ""
    return dt.strftime("%Y-%m-%d")

def load_json(path: Union[str, Path]) -> Union[dict, list]:
    """Load JSON file, return empty dict if not found."""
    p = Path(path)
    if not p.exists():
        return {}
    try:
        with open(p, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Failed to load JSON from {path}: {e}")
        return {}

def save_json(path: Union[str, Path], data: Union[dict, list]) -> None:
    """Save data to JSON file."""
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    try:
        with open(p, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
    except Exception as e:
        logger.error(f"Failed to save JSON to {path}: {e}")

def get_file_extension(filename: str) -> str:
    """Get the file extension in lowercase without dot."""
    if not filename or '.' not in filename:
        return ""
    return filename.rsplit('.', 1)[-1].lower()

def validate_file(uploaded_file: Any, allowed_types: list[str], max_size_mb: int) -> Tuple[bool, str]:
    """Validate uploaded file by extension and size.
    uploaded_file should have .name and .size attributes (like Streamlit UploadedFile).
    """
    if not uploaded_file:
        return False, "No file provided."
    
    ext = get_file_extension(uploaded_file.name)
    if ext not in allowed_types:
        return False, f"Unsupported file type '{ext}'. Allowed types: {', '.join(allowed_types)}"
    
    size_mb = uploaded_file.size / (1024 * 1024)
    if size_mb > max_size_mb:
        return False, f"File size ({size_mb:.1f}MB) exceeds limit of {max_size_mb}MB."
    
    return True, "File is valid."
