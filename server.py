"""
Arxiv Server
===============

This module implements the server for interacting with arXiv.
"""

import logging
from fastapi import FastAPI, HTTPException
from typing import Dict, Any, List
from .config import Settings
from .types import Tool, TextContent, Resource
from .tools import handle_search, handle_download, handle_list_papers, handle_read_paper

# Constants
SERVER_TITLE = "arXiv Research Server"
DEFAULT_RELEVANCE_SCORE = 0.5
LOGGER_NAME = "arxiv-server"

settings = Settings()
logger = logging.getLogger(LOGGER_NAME)
logger.setLevel(logging.INFO)
app = FastAPI(title=SERVER_TITLE)

# Initialize relevance scorer
relevance_scorer = None


def _initialize_relevance_scorer() -> None:
    """Initialize the relevance scorer if OpenAI API key is available."""
    global relevance_scorer
    try:
        from .services.relevance import RelevanceScorer
        if hasattr(settings, 'OPENAI_API_KEY') and settings.OPENAI_API_KEY:
            relevance_scorer = RelevanceScorer(settings.OPENAI_API_KEY)
            logger.info("Relevance scorer initialized successfully")
        else:
            logger.warning("OpenAI API key not found in settings")
    except ImportError as e:
        logger.warning(f"Could not import RelevanceScorer: {e}")
    except Exception as e:
        logger.error(f"Error initializing relevance scorer: {e}")


def _validate_relevance_request(request: Dict[str, Any]) -> tuple[str, Dict[str, Any], str]:
    """Validate relevance calculation request and return query, paper_data, and error message."""
    query = request.get("query", "")
    paper_data = request.get("paper_data", {})
    
    if not relevance_scorer:
        return query, paper_data, "OpenAI API key not configured"
    
    if not query or not paper_data:
        return query, paper_data, "Missing query or paper_data"
    
    return query, paper_data, None


def _create_relevance_response(status: str, score: float = DEFAULT_RELEVANCE_SCORE, 
                              message: str = None) -> Dict[str, Any]:
    """Create standardized relevance response."""
    response = {"status": status, "score": score}
    if message:
        response["message"] = message
    return response


def _get_available_tools() -> Dict[str, Any]:
    """Get dictionary of available tools."""
    return {
        "search": handle_search,
        "download": handle_download,
        "download_paper": handle_download,
        "list_papers": handle_list_papers,
        "read_paper": handle_read_paper,
        "calculate_relevance": calculate_relevance
    }


# Initialize components
_initialize_relevance_scorer()


@app.get("/")
async def root():
    """Root endpoint providing server status."""
    return {"message": "arXiv Server is running"}


@app.post("/tools/calculate_relevance")
async def calculate_relevance(request: Dict[str, Any]):
    """Calculate relevance score between query and paper."""
    try:
        query, paper_data, error_message = _validate_relevance_request(request)
        
        if error_message:
            return _create_relevance_response("error", message=error_message)
        
        score = await relevance_scorer.score_paper(query, paper_data)
        return _create_relevance_response("success", score=score)
        
    except Exception as e:
        logger.error(f"Error calculating relevance: {e}")
        return _create_relevance_response("error", message=str(e))


@app.post("/tools/{tool_name}")
async def handle_tool(tool_name: str, arguments: Dict[str, Any]):
    """Handle tool calls."""
    tools = _get_available_tools()

    if tool_name not in tools:
        raise HTTPException(status_code=404, detail="Tool not found")

    return await tools[tool_name](arguments)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "message": "Server is running properly"}
