"""List functionality for the arXiv MCP server."""

import json
from pathlib import Path
import arxiv
from typing import Dict, Any, List, Optional
import mcp.types as types
from ..config import Settings

settings = Settings()

# Constants
MARKDOWN_EXTENSION = "*.md"
JSON_INDENT = 2

list_tool = types.Tool(
    name="list_papers",
    description="List all existing papers available as resources",
    inputSchema={
        "type": "object",
        "properties": {},
        "required": [],
    },
)


def _get_storage_path() -> Path:
    """Get the storage path."""
    return Path(settings.STORAGE_PATH)


def _extract_paper_ids() -> List[str]:
    """Extract paper IDs from markdown files in storage."""
    storage_path = _get_storage_path()
    return [p.stem for p in storage_path.glob(MARKDOWN_EXTENSION)]


def _create_paper_info(result: arxiv.Result) -> Dict[str, Any]:
    """Create paper information dictionary from arXiv result."""
    return {
        "title": result.title,
        "summary": result.summary,
        "authors": [author.name for author in result.authors],
        "links": [link.href for link in result.links],
        "pdf_url": result.pdf_url,
    }


def _create_response_data(papers: List[str], results: List[arxiv.Result]) -> Dict[str, Any]:
    """Create response data structure."""
    return {
        "total_papers": len(papers),
        "papers": [_create_paper_info(result) for result in results],
    }


def _create_error_response(error_message: str) -> List[types.TextContent]:
    """Create standardized error response."""
    return [types.TextContent(type="text", text=f"Error: {error_message}")]


def _create_success_response(response_data: Dict[str, Any]) -> List[types.TextContent]:
    """Create standardized success response."""
    return [
        types.TextContent(
            type="text", 
            text=json.dumps(response_data, indent=JSON_INDENT)
        )
    ]


def list_papers() -> List[str]:
    """List all stored paper IDs."""
    return _extract_paper_ids()


async def handle_list_papers(
    arguments: Optional[Dict[str, Any]] = None,
) -> List[types.TextContent]:
    """Handle requests to list all stored papers."""
    try:
        papers = list_papers()
        client = arxiv.Client()
        results = client.results(arxiv.Search(id_list=papers))
        response_data = _create_response_data(papers, list(results))
        return _create_success_response(response_data)

    except Exception as e:
        return _create_error_response(str(e))
