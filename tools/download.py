"""Download functionality for the arXiv MCP server."""

import arxiv
import json
import asyncio
import aiofiles
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime
from .. import types
from ..config import Settings
import pymupdf4llm
import logging

logger = logging.getLogger("arxiv-mcp-server")
settings = Settings()

# Constants
PDF_EXTENSION = ".pdf"
MARKDOWN_EXTENSION = ".md"
ENCODING = "utf-8"
STATUS_DOWNLOADING = "downloading"
STATUS_CONVERTING = "converting"
STATUS_SUCCESS = "success"
STATUS_ERROR = "error"

# Global dictionary to track conversion status
conversion_statuses: Dict[str, Any] = {}


@dataclass
class ConversionStatus:
    """Track the status of a PDF to Markdown conversion."""
    paper_id: str
    status: str  # 'downloading', 'converting', 'success', 'error'
    started_at: datetime
    completed_at: Optional[datetime] = None
    error: Optional[str] = None


download_tool = types.Tool(
    name="download_paper",
    description="Download a paper and create a resource for it",
    inputSchema={
        "type": "object",
        "properties": {
            "paper_id": {
                "type": "string",
                "description": "The arXiv ID of the paper to download",
            },
            "check_status": {
                "type": "boolean",
                "description": "If true, only check conversion status without downloading",
                "default": False,
            },
        },
        "required": ["paper_id"],
    },
)


def _ensure_storage_path() -> Path:
    """Ensure storage directory exists and return the path."""
    storage_path = Path(settings.STORAGE_PATH)
    storage_path.mkdir(parents=True, exist_ok=True)
    return storage_path


def get_paper_path(paper_id: str, suffix: str = MARKDOWN_EXTENSION) -> Path:
    """Get the absolute file path for a paper with given suffix."""
    storage_path = _ensure_storage_path()
    return storage_path / f"{paper_id}{suffix}"


def _validate_pdf_file(pdf_path: Path) -> None:
    """Validate that PDF file exists and is readable."""
    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF file not found at {pdf_path}")


def _validate_conversion_result(markdown: str) -> None:
    """Validate that conversion produced content."""
    if not markdown:
        raise ValueError("PDF conversion resulted in empty content")


def _update_conversion_status(paper_id: str, status: str, error: str = None) -> None:
    """Update the conversion status for a paper."""
    conversion_status = conversion_statuses.get(paper_id)
    if conversion_status:
        conversion_status.status = status
        conversion_status.completed_at = datetime.now()
        if error:
            conversion_status.error = error


async def _write_markdown_file(content: str, file_path: Path) -> None:
    """Write markdown content to file."""
    async with aiofiles.open(file_path, "w", encoding=ENCODING) as f:
        await f.write(content)


async def convert_pdf_to_markdown(paper_id: str, pdf_path: Path) -> None:
    """Convert PDF to Markdown in a separate thread."""
    try:
        logger.info(f"Starting conversion for {paper_id}")
        
        _validate_pdf_file(pdf_path)
            
        # Execute the conversion in a separate thread to avoid blocking
        markdown = await asyncio.to_thread(
            pymupdf4llm.to_markdown,
            str(pdf_path),
            show_progress=False
        )
        
        _validate_conversion_result(markdown)

        md_path = get_paper_path(paper_id, MARKDOWN_EXTENSION)
        await _write_markdown_file(markdown, md_path)

        _update_conversion_status(paper_id, STATUS_SUCCESS)
        logger.info(f"Conversion completed for {paper_id}")

    except Exception as e:
        logger.error(f"Conversion failed for {paper_id}: {str(e)}")
        _update_conversion_status(paper_id, STATUS_ERROR, str(e))
        raise


async def handle_download(arguments: Dict[str, Any]) -> List[types.TextContent]:
    """Handle paper download and conversion requests."""
    paper_id = arguments["paper_id"]
    check_status = arguments.get("check_status", False)

    try:
        # Ensure storage directory exists
        storage_path = Path(settings.STORAGE_PATH)
        storage_path.mkdir(parents=True, exist_ok=True)
        
        pdf_path = storage_path / f"{paper_id}.pdf"
        md_path = storage_path / f"{paper_id}.md"

        # Check status if requested
        if check_status:
            if md_path.exists():
                return [types.TextContent(
                    text=json.dumps({
                        "status": "success",
                        "message": "Paper already downloaded and converted",
                        "resource_uri": f"file://{get_paper_path(paper_id, '.md')}",
                    })
                )]
            
            current_status = conversion_statuses.get(paper_id)
            if current_status:
                return [types.TextContent(
                    text=json.dumps({
                        "status": current_status.status,
                        "message": f"Conversion status for {paper_id}: {current_status.status}",
                        "started_at": current_status.started_at.isoformat(),
                        "completed_at": current_status.completed_at.isoformat() if current_status.completed_at else None,
                        "error": current_status.error,
                    })
                )]
            
            return [types.TextContent(
                text=json.dumps({
                    "status": "not_found",
                    "message": f"Paper {paper_id} not found or no conversion initiated.",
                })
            )]

        # Check if paper is already being processed
        if paper_id in conversion_statuses:
            current_status = conversion_statuses[paper_id]
            if current_status.status == "success" and md_path.exists():
                return [types.TextContent(
                    text=json.dumps({
                        "status": "success",
                        "message": "Paper already downloaded and converted",
                        "resource_uri": f"file://{get_paper_path(paper_id, '.md')}",
                    })
                )]
            elif current_status.status in ["downloading", "converting"]:
                return [types.TextContent(
                    text=json.dumps({
                        "status": "in_progress",
                        "message": f"Conversion for {paper_id} already in progress ({current_status.status})",
                        "started_at": current_status.started_at.isoformat(),
                    })
                )]

        # Create new conversion status
        status = ConversionStatus(
            paper_id=paper_id,
            status="downloading",
            started_at=datetime.now()
        )
        conversion_statuses[paper_id] = status

        try:
            # Search for paper
            search = arxiv.Search(id_list=[paper_id])
            paper = next(search.results())
            
            # Create parent directory if it doesn't exist
            pdf_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Download PDF with error handling
            try:
                paper.download_pdf(filename=str(pdf_path))
                logger.info(f"PDF downloaded for {paper_id} to {pdf_path}")
            except Exception as download_error:
                raise Exception(f"Failed to download PDF: {str(download_error)}")

            # Update status to converting
            status.status = "converting"

            # Convert to markdown with proper error handling
            try:
                await convert_pdf_to_markdown(paper_id, pdf_path)
                status.status = "success"
                status.completed_at = datetime.now()

                return [types.TextContent(
                    text=json.dumps({
                        "status": "success",
                        "message": "Paper downloaded and converted successfully",
                        "resource_uri": f"file://{get_paper_path(paper_id, '.md')}",
                        "started_at": status.started_at.isoformat(),
                        "completed_at": status.completed_at.isoformat(),
                    })
                )]
            except Exception as conv_error:
                status.status = "error"
                status.completed_at = datetime.now()
                status.error = f"Conversion error: {str(conv_error)}"
                raise Exception(f"Failed to convert PDF to markdown: {str(conv_error)}")

        except StopIteration:
            status.status = "error"
            status.completed_at = datetime.now()
            status.error = f"Paper {paper_id} not found on arXiv"
            return [types.TextContent(
                text=json.dumps({
                    "status": "error",
                    "message": f"Paper {paper_id} not found on arXiv",
                })
            )]
        
        except Exception as e:
            status.status = "error"
            status.completed_at = datetime.now()
            status.error = str(e)
            raise

    except Exception as e:
        error_msg = f"Error during download or conversion: {str(e)}"
        logger.error(error_msg)
        return [types.TextContent(
            text=json.dumps({
                "status": "error",
                "message": error_msg,
            })
        )]
