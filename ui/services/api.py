import httpx
from typing import Dict, Any, List, Optional
from ..config import UISettings
import asyncio
import json

# Constants
HEALTH_ENDPOINT = "/health"
SEARCH_ENDPOINT = "/tools/search"
DOWNLOAD_ENDPOINT = "/tools/download"
RELEVANCE_ENDPOINT = "/tools/calculate_relevance"
HEALTH_CHECK_TIMEOUT = 5.0
REQUEST_TIMEOUT = 30.0
HTTP_OK = 200

class ArxivAPIService:
    """Service for interacting with the arXiv API through the backend server."""
    
    def __init__(self):
        self.settings = UISettings()
        self.base_url = self.settings.API_URL
        self._is_server_running = False

    def _create_error_response(self, message: str, papers: List = None) -> Dict[str, Any]:
        """Create standardized error response."""
        response = {"status": "error", "message": message}
        if papers is not None:
            response["papers"] = papers
        return response

    def _create_success_response(self, message: str = None, **kwargs) -> Dict[str, Any]:
        """Create standardized success response."""
        response = {"status": "success"}
        if message:
            response["message"] = message
        response.update(kwargs)
        return response

    async def _make_request(self, method: str, endpoint: str, data: Dict = None, timeout: float = REQUEST_TIMEOUT) -> httpx.Response:
        """Make HTTP request with error handling."""
        async with httpx.AsyncClient() as client:
            if method.upper() == "GET":
                response = await client.get(f"{self.base_url}{endpoint}", timeout=timeout)
            elif method.upper() == "POST":
                response = await client.post(f"{self.base_url}{endpoint}", json=data, timeout=timeout)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            response.raise_for_status()
            return response

    async def check_server_health(self) -> bool:
        """Check if the backend server is running and healthy."""
        try:
            response = await self._make_request("GET", HEALTH_ENDPOINT, timeout=HEALTH_CHECK_TIMEOUT)
            self._is_server_running = response.status_code == HTTP_OK
            return self._is_server_running
        except Exception:
            self._is_server_running = False
            return False

    async def ensure_server_running(self) -> bool:
        """Ensure the server is running before making a request."""
        if not self._is_server_running:
            return await self.check_server_health()
        return True

    def _prepare_search_data(self, query: str, category: str = None) -> Dict[str, Any]:
        """Prepare search request data."""
        data = {"query": query}
        if category:
            data["category"] = category
        return data

    async def search_papers(self, query: str, category: str = None) -> Dict[str, Any]:
        """Search for papers using the backend API."""
        if not await self.ensure_server_running():
            return self._create_error_response(
                "Backend server is not running. Please start the server first.",
                papers=[]
            )

        try:
            data = self._prepare_search_data(query, category)
            response = await self._make_request("POST", SEARCH_ENDPOINT, data)
            results = response.json()
            
            return self._create_success_response(
                message=f"Found {len(results)} papers",
                papers=results
            )
            
        except httpx.HTTPStatusError as e:
            return self._create_error_response(
                f"Server error: {e.response.status_code} - {e.response.text}",
                papers=[]
            )
        except httpx.RequestError as e:
            return self._create_error_response(f"Connection error: {str(e)}", papers=[])
        except Exception as e:
            return self._create_error_response(f"Unexpected error: {str(e)}", papers=[])

    def _parse_download_response(self, raw_response) -> Dict[str, Any]:
        """Parse download response from server."""
        # If server returned a list of TextContent, extract the JSON from the first item's text
        if isinstance(raw_response, list) and raw_response:
            first = raw_response[0]
            text = first.get('text')
            if text:
                try:
                    return json.loads(text)
                except json.JSONDecodeError:
                    return self._create_error_response("Failed to parse download response")
        # Otherwise return raw response
        return raw_response

    async def download_paper(self, paper_id: str) -> Dict[str, Any]:
        """Request paper download through the backend API."""
        if not await self.ensure_server_running():
            return self._create_error_response(
                "Backend server is not running. Please start the server first."
            )

        try:
            response = await self._make_request("POST", DOWNLOAD_ENDPOINT, {"paper_id": paper_id})
            raw = response.json()
            return self._parse_download_response(raw)
            
        except httpx.HTTPStatusError as e:
            return self._create_error_response(
                f"Server error: {e.response.status_code} - {e.response.text}"
            )
        except httpx.RequestError as e:
            return self._create_error_response(f"Connection error: {str(e)}")
        except Exception as e:
            return self._create_error_response(f"Unexpected error: {str(e)}")

    async def calculate_relevance(self, query: str, paper_data: Dict[str, str]) -> Dict[str, Any]:
        """Calculate relevance score for a paper against the search query."""
        if not await self.ensure_server_running():
            return self._create_error_response("Backend server is not running", score=0.5)

        try:
            data = {"query": query, "paper_data": paper_data}
            response = await self._make_request("POST", RELEVANCE_ENDPOINT, data)
            return response.json()
            
        except Exception as e:
            return {"status": "error", "score": 0.5, "message": str(e)}