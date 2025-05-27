from dataclasses import dataclass
from typing import Dict, Any, Optional

@dataclass
class TextContent:
    """Text content with metadata."""
    text: str
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class Tool:
    """Tool definition."""
    name: str
    description: str
    inputSchema: Dict[str, Any]

@dataclass
class Resource:
    """Resource definition for papers."""
    uri: str
    name: str
    description: str
    mimeType: str = "application/pdf"
    metadata: Optional[Dict[str, Any]] = None