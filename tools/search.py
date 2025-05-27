"""Search functionality for the arXiv MCP server."""

import logging
from typing import Dict, Any, List
import arxiv
from ..types import Tool, TextContent

logger = logging.getLogger(__name__)

# Constants
DEFAULT_MAX_RESULTS = 10
DEFAULT_CATEGORY = "cs.AI"

search_tool = Tool(
    name="search",
    description="Search for papers on arXiv",
    inputSchema={
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Search query"
            },
            "max_results": {
                "type": "integer",
                "description": "Maximum number of results",
                "default": DEFAULT_MAX_RESULTS
            },
            "category": {
                "type": "string",
                "description": "arXiv category to search in",
                "default": DEFAULT_CATEGORY
            }
        },
        "required": ["query"]
    }
)


def _extract_paper_id(entry_id: str) -> str:
    """Extract paper ID from entry ID."""
    return entry_id.split("/")[-1]


def _create_paper_data(result: arxiv.Result, category: str) -> Dict[str, Any]:
    """Create standardized paper data dictionary."""
    return {
        "id": _extract_paper_id(result.entry_id),
        "title": result.title,
        "authors": [author.name for author in result.authors],
        "abstract": result.summary,
        "category": category,
        "url": result.pdf_url
    }


def _create_search_query(query: str, max_results: int) -> arxiv.Search:
    """Create arXiv search query with standardized parameters."""
    return arxiv.Search(
        query=query,
        max_results=max_results,
        sort_by=arxiv.SortCriterion.Relevance
    )


def _process_search_results(search_results, category: str) -> List[TextContent]:
    """Process search results into standardized format."""
    results = []
    for result in search_results:
        paper_data = _create_paper_data(result, category)
        results.append(TextContent(
            text=str(paper_data),
            metadata=paper_data
        ))
    return results


async def handle_search(arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle search requests."""
    query = arguments["query"]
    max_results = arguments.get("max_results", DEFAULT_MAX_RESULTS)
    category = arguments.get("category", DEFAULT_CATEGORY)

    search = _create_search_query(query, max_results)
    search_results = search.results()
    
    return _process_search_results(search_results, category)
