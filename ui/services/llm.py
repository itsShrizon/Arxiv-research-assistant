import httpx
from typing import Dict, Any
from arxiv_mcp_server.ui.config import UISettings

class LLMService:
    """Service for LLM-based paper analysis through the backend server."""
    
    def __init__(self):
        self.settings = UISettings()
        self.base_url = self.settings.API_URL

    async def analyze_paper(self, paper_id: str, prompt: str = None) -> Dict[str, Any]:
        """Analyze a paper using the backend API."""
        async with httpx.AsyncClient() as client:
            try:
                data = {"paper_id": paper_id}
                if prompt:
                    data["prompt"] = prompt

                response = await client.post(
                    f"{self.base_url}/tools/read_paper",
                    json=data,
                    timeout=60.0
                )
                response.raise_for_status()
                return response.json()
            except httpx.HTTPError as e:
                print(f"HTTP error occurred while analyzing paper: {e}")
                return {"status": "error", "message": str(e)}
            except Exception as e:
                print(f"Error occurred while analyzing paper: {e}")
                return {"status": "error", "message": str(e)}