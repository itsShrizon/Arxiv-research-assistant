"""Utility functions for the arXiv MCP server."""

import json
from typing import Dict, Any, List
from pathlib import Path

# Constants
MARKDOWN_EXTENSION = ".md"
PDF_EXTENSION = ".pdf"
JSON_EXTENSION = ".json"
DEFAULT_ENCODING = "utf-8"

# HTTP status codes
HTTP_OK = 200
HTTP_NOT_FOUND = 404
HTTP_SERVER_ERROR = 500

# Response statuses
STATUS_SUCCESS = "success"
STATUS_ERROR = "error"

# Relevance scoring
DEFAULT_RELEVANCE_SCORE = 0.5
HIGH_RELEVANCE_THRESHOLD = 0.7
MEDIUM_RELEVANCE_THRESHOLD = 0.5


# File and Path Utilities
def ensure_directory_exists(path: Path) -> Path:
    """Ensure a directory exists, creating it if necessary."""
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_file_extension(file_path: Path) -> str:
    """Get the file extension from a path."""
    return file_path.suffix


def change_file_extension(file_path: Path, new_extension: str) -> Path:
    """Change the extension of a file path."""
    return file_path.with_suffix(new_extension)


def get_paper_file_path(directory: Path, paper_id: str, extension: str = MARKDOWN_EXTENSION) -> Path:
    """Get standardized file path for a paper."""
    return directory / f"{paper_id}{extension}"


def safe_read_file(file_path: Path, encoding: str = DEFAULT_ENCODING) -> str:
    """Safely read file content, return empty string if failed."""
    try:
        if file_path.exists():
            with open(file_path, "r", encoding=encoding) as f:
                return f.read()
    except Exception:
        pass
    return ""


def safe_write_file(file_path: Path, content: str, encoding: str = DEFAULT_ENCODING) -> bool:
    """Safely write content to file, return success status."""
    try:
        ensure_directory_exists(file_path.parent)
        with open(file_path, "w", encoding=encoding) as f:
            f.write(content)
        return True
    except Exception:
        return False


# JSON Utilities
def safe_json_loads(text: str, default: Any = None) -> Any:
    """Safely parse JSON, returning default value on error."""
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return default


def safe_json_dumps(data: Any, indent: int = None) -> str:
    """Safely serialize to JSON, returning empty string on error."""
    try:
        return json.dumps(data, indent=indent)
    except (TypeError, ValueError):
        return ""


def safe_read_json(file_path: Path) -> Dict[str, Any]:
    """Safely read JSON file, return empty dict if failed."""
    content = safe_read_file(file_path)
    return safe_json_loads(content, {})


def safe_write_json(file_path: Path, data: Dict[str, Any], indent: int = 2) -> bool:
    """Safely write JSON data to file, return success status."""
    content = safe_json_dumps(data, indent=indent)
    return safe_write_file(file_path, content) if content else False


# Response Utilities
def create_error_response(message: str, **kwargs) -> Dict[str, Any]:
    """Create a standardized error response."""
    response = {"status": STATUS_ERROR, "message": message}
    response.update(kwargs)
    return response


def create_success_response(message: str = None, **kwargs) -> Dict[str, Any]:
    """Create a standardized success response."""
    response = {"status": STATUS_SUCCESS}
    if message:
        response["message"] = message
    response.update(kwargs)
    return response


# List and Collection Utilities
def safe_get_first(items: List[Any], default: Any = None) -> Any:
    """Safely get the first item from a list."""
    return items[0] if items else default


def chunk_list(items: List[Any], chunk_size: int) -> List[List[Any]]:
    """Split a list into chunks of specified size."""
    return [items[i:i + chunk_size] for i in range(0, len(items), chunk_size)]


def filter_none_values(data: Dict[str, Any]) -> Dict[str, Any]:
    """Remove keys with None values from a dictionary."""
    return {k: v for k, v in data.items() if v is not None}


# String Utilities
def truncate_string(text: str, max_length: int, suffix: str = "...") -> str:
    """Truncate a string to a maximum length with optional suffix."""
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def clean_whitespace(text: str) -> str:
    """Clean and normalize whitespace in text."""
    return " ".join(text.split())


def extract_paper_id(entry_id: str) -> str:
    """Extract paper ID from arXiv entry ID."""
    return entry_id.split("/")[-1]


# Validation Utilities
def is_valid_paper_id(paper_id: str) -> bool:
    """Check if a paper ID appears to be valid."""
    if not paper_id:
        return False
    # Basic format check for arXiv IDs
    return len(paper_id.split('.')) >= 2 and any(c.isdigit() for c in paper_id)


def validate_required_fields(data: Dict[str, Any], required_fields: List[str]) -> List[str]:
    """Validate that required fields are present and non-empty."""
    missing = []
    for field in required_fields:
        if field not in data or not data[field]:
            missing.append(field)
    return missing


# Relevance scoring helpers
def get_relevance_level(score: float) -> str:
    """Get text description of relevance level."""
    if score >= HIGH_RELEVANCE_THRESHOLD:
        return "High"
    elif score >= MEDIUM_RELEVANCE_THRESHOLD:
        return "Medium"
    else:
        return "Low"


def get_relevance_emoji(score: float) -> str:
    """Get emoji for relevance score."""
    if score >= 0.8:
        return "🔥"
    elif score >= 0.6:
        return "⭐"
    elif score >= 0.4:
        return "👍"
    else:
        return "👎"


def get_relevance_color(score: float) -> str:
    """Get color classification for relevance score."""
    if score >= HIGH_RELEVANCE_THRESHOLD:
        return "success"
    elif score >= MEDIUM_RELEVANCE_THRESHOLD:
        return "warning"
    else:
        return "error"
