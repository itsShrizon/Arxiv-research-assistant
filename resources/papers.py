"""Resource management and storage for arXiv papers."""

from pathlib import Path
from typing import List
import arxiv
import pymupdf4llm
import aiofiles
import logging
from pydantic import AnyUrl
import mcp.types as types
from ..config import Settings

logger = logging.getLogger("arxiv-mcp-server")

# Constants
MARKDOWN_EXTENSION = ".md"
PDF_EXTENSION = ".pdf"
ENCODING = "utf-8"


class PaperManager:
    """Manages the storage, retrieval, and resource handling of arXiv papers."""

    def __init__(self):
        """Initialize the paper management system."""
        settings = Settings()
        self.storage_path = Path(settings.STORAGE_PATH)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.client = arxiv.Client()

    def _get_paper_path(self, paper_id: str, extension: str = MARKDOWN_EXTENSION) -> Path:
        """Get the absolute file path for a paper with specified extension."""
        return self.storage_path / f"{paper_id}{extension}"

    def _get_paper_from_arxiv(self, paper_id: str) -> arxiv.Result:
        """Fetch paper metadata from arXiv."""
        try:
            return next(self.client.results(arxiv.Search(id_list=[paper_id])))
        except StopIteration:
            raise ValueError(f"Paper with ID {paper_id} not found on arXiv.")

    async def _download_paper_pdf(self, paper: arxiv.Result, pdf_path: Path) -> None:
        """Download paper PDF to specified path."""
        try:
            paper.download_pdf(dirpath=self.storage_path, filename=pdf_path)
        except arxiv.ArxivError as e:
            raise ValueError(f"Error: Failed to download paper {paper.entry_id} from arXiv. Details: {str(e)}")

    async def _convert_pdf_to_markdown(self, pdf_path: Path) -> str:
        """Convert PDF file to markdown format."""
        try:
            return pymupdf4llm.to_markdown(pdf_path, show_progress=False)
        except Exception as e:
            raise ValueError(f"Error: Failed to convert PDF to markdown. Details: {str(e)}")

    async def _save_markdown_content(self, content: str, md_path: Path) -> None:
        """Save markdown content to file."""
        try:
            async with aiofiles.open(md_path, "w", encoding=ENCODING) as f:
                await f.write(content)
        except Exception as e:
            raise ValueError(f"Error: Failed to save markdown file. Details: {str(e)}")

    async def store_paper(self, paper_id: str, pdf_url: str) -> bool:
        """Download and store a paper from arXiv."""
        paper_md_path = self._get_paper_path(paper_id, MARKDOWN_EXTENSION)

        # Return early if paper already exists
        if paper_md_path.exists():
            return True

        try:
            paper_pdf_path = self._get_paper_path(paper_id, PDF_EXTENSION)

            # Get paper metadata
            paper = self._get_paper_from_arxiv(paper_id)

            # Download PDF
            await self._download_paper_pdf(paper, paper_pdf_path)

            # Convert to markdown
            markdown = await self._convert_pdf_to_markdown(paper_pdf_path)

            # Save markdown
            await self._save_markdown_content(markdown, paper_md_path)

            return True

        except Exception as e:
            # Re-raise with context if it's already a ValueError, otherwise wrap it
            if isinstance(e, ValueError):
                raise
            raise ValueError(f"Error: An unexpected error occurred while storing paper {paper_id}. Details: {str(e)}")

    async def has_paper(self, paper_id: str) -> bool:
        """Check if a paper is available in storage."""
        return self._get_paper_path(paper_id).exists()

    async def list_papers(self) -> list[str]:
        """List all stored paper IDs."""
        logger.info(f"Listing papers in {self.storage_path}")
        paper_ids = [p.stem for p in self.storage_path.glob(f"*{MARKDOWN_EXTENSION}")]
        logger.info(f"Found {len(paper_ids)} papers")
        return paper_ids

    def _create_resource_from_paper(self, paper: arxiv.Result, paper_path: Path) -> types.Resource:
        """Create a resource object from paper metadata."""
        return types.Resource(
            uri=AnyUrl(f"file://{str(paper_path)}"),
            name=paper.title,
            description=paper.summary,
            mimeType="text/markdown",
        )

    async def list_resources(self) -> List[types.Resource]:
        """List all papers as MCP resources with metadata."""
        paper_ids = await self.list_papers()
        resources = []

        for paper_id in paper_ids:
            try:
                search = arxiv.Search(id_list=[paper_id])
                papers = list(self.client.results(search))

                if papers:
                    paper = papers[0]
                    paper_path = self._get_paper_path(paper_id)
                    resource = self._create_resource_from_paper(paper, paper_path)
                    resources.append(resource)
            except Exception as e:
                logger.warning(f"Failed to create resource for paper {paper_id}: {e}")

        logger.info(f"Found {len(resources)} resources")
        return resources

    async def get_paper_content(self, paper_id: str) -> str:
        """Get the markdown content of a stored paper."""
        paper_path = self._get_paper_path(paper_id)
        if not paper_path.exists():
            raise ValueError(f"Paper {paper_id} not found in storage")

        async with aiofiles.open(paper_path, "r", encoding=ENCODING) as f:
            return await f.read()
