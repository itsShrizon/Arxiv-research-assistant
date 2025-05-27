"""Configuration settings for the arXiv MCP server."""

import sys
import argparse
from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path
import logging
from typing import Optional

logger = logging.getLogger(__name__)

# Default configuration constants
DEFAULT_APP_NAME = "arxiv-mcp-server"
DEFAULT_APP_VERSION = "0.2.10"
DEFAULT_MAX_RESULTS = 50
DEFAULT_BATCH_SIZE = 20
DEFAULT_REQUEST_TIMEOUT = 60
DEFAULT_HOST = "0.0.0.0"
DEFAULT_PORT = 8000
DEFAULT_API_URL = "http://localhost:8000"
DEFAULT_STORAGE_PATH = "./data/papers"
DEFAULT_PDF_CONVERSION_THREADS = 4
DEFAULT_ENV_FILE = ".env"
DEFAULT_ENCODING = "utf-8"


class Settings(BaseSettings):
    """Server configuration settings."""

    APP_NAME: str = DEFAULT_APP_NAME
    APP_VERSION: str = DEFAULT_APP_VERSION
    MAX_RESULTS: int = DEFAULT_MAX_RESULTS
    BATCH_SIZE: int = DEFAULT_BATCH_SIZE
    REQUEST_TIMEOUT: int = DEFAULT_REQUEST_TIMEOUT
    HOST: str = DEFAULT_HOST
    PORT: int = DEFAULT_PORT

    # API Configuration
    API_URL: str = DEFAULT_API_URL
    OPENAI_API_KEY: str
    DEBUG: bool = False

    # Storage Configuration
    STORAGE_PATH: str = DEFAULT_STORAGE_PATH
    PDF_CONVERSION_THREADS: int = DEFAULT_PDF_CONVERSION_THREADS

    model_config = SettingsConfigDict(
        env_file=DEFAULT_ENV_FILE,
        env_file_encoding=DEFAULT_ENCODING,
        extra="allow"
    )

    def _create_argument_parser(self) -> argparse.ArgumentParser:
        """Create argument parser for command line options."""
        parser = argparse.ArgumentParser()
        parser.add_argument("--storage-path", type=str, help="Custom storage path for papers")
        return parser

    def _get_storage_path_from_args(self) -> Optional[Path]:
        """Get storage path from command line arguments."""
        parser = self._create_argument_parser()
        args, _ = parser.parse_known_args()
        return Path(args.storage_path) if args.storage_path else None

    def _ensure_storage_directory(self, path: Path) -> Path:
        """Ensure storage directory exists."""
        path.mkdir(parents=True, exist_ok=True)
        return path

    @property
    def storage_path(self) -> Path:
        """Get the storage path, ensuring it exists."""
        path = self._get_storage_path_from_args() or Path(self.STORAGE_PATH)
        return self._ensure_storage_directory(path)
