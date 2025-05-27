"""Standalone entry point for the Streamlit UI."""

import os
import sys
from pathlib import Path

# Add the project root to Python path
project_root = str(Path(__file__).parent.parent.parent.parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from arxiv_mcp_server.ui.app import main

if __name__ == "__main__":
    main()
