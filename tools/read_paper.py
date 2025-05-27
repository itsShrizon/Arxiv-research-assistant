"""Tool for reading downloaded papers."""

import json
from pathlib import Path
from typing import Dict, Any, List
from ..types import Tool, TextContent
from ..config import Settings
from ..utils import (
    MARKDOWN_EXTENSION, 
    DEFAULT_ENCODING, 
    create_error_response, 
    create_success_response,
    get_paper_file_path,
    safe_read_file
)

settings = Settings()

read_paper_tool = Tool(
    name="read_paper",
    description="Read the content of a downloaded paper",
    inputSchema={
        "type": "object",
        "properties": {
            "paper_id": {
                "type": "string",
                "description": "The arXiv ID of the paper to read",
            }
        },
        "required": ["paper_id"],
    },
)


def _create_error_response(message: str) -> List[TextContent]:
    """Create a standardized error response."""
    return [
        TextContent(
            text=json.dumps(
                {
                    "status": "error",
                    "message": message,
                }
            )
        )
    ]


def _create_success_response(
    content: str, paper_id: str, paper_path: Path
) -> List[TextContent]:
    """Create a standardized success response."""
    return [
        TextContent(
            text=content,
            metadata={
                "paper_id": paper_id,
                "path": str(paper_path),
                "format": "markdown",
            },
        )
    ]


def _get_paper_path(paper_id: str) -> Path:
    """Get the file path for a paper."""
    return get_paper_file_path(Path(settings.STORAGE_PATH), paper_id, MARKDOWN_EXTENSION)


def _read_paper_file(paper_path: Path) -> str:
    """Read paper content from file."""
    with open(paper_path, "r", encoding=ENCODING) as f:
        return f.read()


async def handle_read_paper(arguments: Dict[str, Any]) -> List[TextContent]:
    """Read a paper's content from storage."""
    paper_id = arguments["paper_id"]
    paper_path = _get_paper_path(paper_id)

    try:
        if not paper_path.exists():
            return _create_error_response(f"Paper {paper_id} not found in storage")

        content = _read_paper_file(paper_path)
        return _create_success_response(content, paper_id, paper_path)

    except Exception as e:
        return _create_error_response(f"Error reading paper: {str(e)}")
