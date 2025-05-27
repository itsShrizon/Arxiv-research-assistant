"""arXiv Server initialization."""
import uvicorn
from .server import app


def main():
    """Start the FastAPI server."""
    uvicorn.run(app, host="0.0.0.0", port=8000)


__all__ = ["main", "app"]
