"""Tools for the arXiv MCP server."""

from .search import search_tool, handle_search
from .download import download_tool, handle_download
from .read_paper import read_paper_tool, handle_read_paper

__all__ = [
    "search_tool",
    "handle_search",
    "download_tool",
    "handle_download",
    "read_paper_tool",
    "handle_read_paper",
    "handle_list_papers"
]

async def handle_list_papers():
    """List available papers."""
    # Implementation will be added later
    return []
