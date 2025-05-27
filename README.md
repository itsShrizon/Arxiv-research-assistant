# arxiv-mcp-server

A unified platform for exploring, analyzing, and interacting with arXiv research papers using a modern web UI and backend server.

## Features
- **Backend API**: Serves arXiv paper data, search, and LLM-powered analysis endpoints
- **Modern UI**: Streamlit app for searching, reading, and analyzing arXiv papers
- **LLM Integration**: Deep research analysis and summarization using language models
- **Paper Management**: Download, list, and read papers in PDF or Markdown
- **History & Relevance**: Track search history and relevance scoring

## Quick Start

1. **Install dependencies**
   ```powershell
   pip install -r requirements.txt
   ```

2. **Run both backend and UI**
   ```powershell
   python src/arxiv_mcp_server/ui/start_services.py
   ```
   - Backend: http://localhost:8000
   - UI: http://localhost:8501

3. **Stop services**
   Press `Ctrl+C` in the terminal to stop both backend and UI.

## Project Structure

```
project-root/
├── README.md
├── requirements.txt
├── pyproject.toml
├── data/
│   └── papers/
├── src/
│   └── arxiv_mcp_server/
│       ├── __init__.py
│       ├── __main__.py
│       ├── config.py
│       ├── server.py
│       ├── types.py
│       ├── models/
│       │   └── history.py
│       ├── prompts/
│       │   ├── __init__.py
│       │   ├── deep_research_analysis_prompt.py
│       │   ├── handlers.py
│       │   ├── prompt_manager.py
│       │   └── prompts.py
│       ├── resources/
│       │   ├── __init__.py
│       │   └── papers.py
│       ├── services/
│       │   ├── __init__.py
│       │   ├── api.py
│       │   ├── llm.py
│       │   └── relevance.py
│       ├── tools/
│       │   ├── __init__.py
│       │   ├── download.py
│       │   ├── list_papers.py
│       │   ├── read_paper.py
│       │   └── search.py
│       └── ui/
│           ├── __init__.py
│           ├── app.py
│           ├── app_clean.py
│           ├── config.py
│           ├── modern_components.py
│           ├── run_ui.py
│           ├── start_services.py
│           ├── STREAMLIT_HTML_SOLUTIONS.md
│           ├── styles.py
│           ├── data/
│           │   ├── arxiv-logo.svg
│           │   └── search_history.json
│           └── services/
│               ├── __init__.py
│               ├── api.py
│               └── llm.py
└── arxiv_mcp_server.egg-info/
    ├── dependency_links.txt
    ├── entry_points.txt
    ├── PKG-INFO
    ├── requires.txt
    ├── SOURCES.txt
    └── top_level.txt
```

## Demo Video

[![Project Demo](https://drive.google.com/file/d/18LjlpyrIzt175p8UOAc_b3oD1BxTZja0/view?usp=sharing)](DRIVE_VIDEO_LINK)

> **Note:** Replace `DRIVE_VIDEO_LINK` with your actual Google Drive video link. The badge above will act as a clickable button to your video.

## Customization
- Add your own LLM API keys and configuration in `src/arxiv_mcp_server/config.py`.
- Place downloaded papers in `data/papers/`.

## License
MIT License
