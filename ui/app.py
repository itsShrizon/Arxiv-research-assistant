import streamlit as st

# Set page config first - this must be the first Streamlit command
st.set_page_config(
    page_title="arXiv Research Assistant",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

import pandas as pd
from datetime import datetime
import plotly.express as px
import asyncio
import json
from pathlib import Path
from arxiv_mcp_server.ui.services.api import ArxivAPIService
from arxiv_mcp_server.ui.services.llm import LLMService
from arxiv_mcp_server.ui.config import UISettings
from styles import main_css

# Cusstom css
st.markdown(main_css, unsafe_allow_html=True)

# Initial setup
ui_settings = UISettings()

def load_search_history() -> list:
    """Load search history from a JSON file."""
    history_file = Path(__file__).parent / "data" / "search_history.json"
    try:
        if history_file.exists():
            with open(history_file, "r") as f:
                return json.load(f)
    except Exception as e:
        st.error(f"Error loading search history: {e}")
    return []

def save_search_history(search_item: dict):
    """Save a search item to the history file."""
    history_file = Path(__file__).parent / "data" / "search_history.json"
    try:
        history = load_search_history()
        history.append(search_item)
        history_file.parent.mkdir(parents=True, exist_ok=True)
        with open(history_file, "w") as f:
            json.dump(history, f)
    except Exception as e:
        st.error(f"Error saving search history: {e}")

def repeat_search(search_item: dict):
    """Repeat a previous search."""
    try:
        query = search_item.get('query', '')
        category = search_item.get('category')
        if query:
            api = get_api_service()
            handle_search(api, query, category)
    except Exception as e:
        st.error(f"Error repeating search: {e}")

# Sidebar Components
def render_sidebar():
    with st.sidebar:
        st.image(r"C:/Users/Etu/Desktop/Personal Projects/arxiv-mcp-server\src/arxiv_mcp_server/ui/data/arxiv-logo.svg", width=120)
        
        st.title("Research Assistant")
        
        # Check server status
        api = get_api_service()
        if asyncio.run(api.check_server_health()):
            st.success("✅ Backend server is running")
        else:
            st.error("❌ Backend server is not running")
            st.warning("""
            Please start the backend server first:
            1. Open a new terminal
            2. Navigate to the project root
            3. Run: `python -m arxiv_mcp_server`
            """)
        
        st.markdown("---")
        
        search_type = st.selectbox(
            "Search Type",
            ["Natural Language", "Category Based", "View History"],
            key="search_type_selector"
        )
        
        return search_type

def handle_search(api: ArxivAPIService, query: str, category: str = None):
    with st.spinner("Searching for papers..."):
        try:
            results = asyncio.run(api.search_papers(query=query, category=category))
            if results["status"] == "success":
                if results["papers"]:
                    papers = []
                    relevance_scores = []
                    paper_ids = []
                    
                    for paper in results["papers"]:
                        metadata = paper.get('metadata', {})
                        # Get relevance score from metadata if available, otherwise calculate it
                        relevance = metadata.get('relevance_score', None)
                        if relevance is None:
                            # Call the backend to calculate relevance
                            paper_data = {
                                'title': metadata.get('title', ''),
                                'abstract': metadata.get('abstract', '')
                            }
                            score_result = asyncio.run(api.calculate_relevance(query, paper_data))
                            relevance = score_result.get('score', 0.5)  # Default to 0.5 if calculation fails
                        
                        papers.append({**metadata, 'relevance_score': relevance})
                        relevance_scores.append(relevance)
                        paper_ids.append(metadata.get('id', ''))
                    
                    # Sort papers by relevance score
                    st.session_state.search_results = sorted(
                        papers,
                        key=lambda x: x['relevance_score'],
                        reverse=True
                    )
                    
                    # Save search to history
                    search_history_item = {
                        'id': datetime.now().timestamp(),
                        'query': query,
                        'category': category,
                        'categories': [category] if category else [],
                        'timestamp': datetime.now().isoformat(),
                        'paper_ids': paper_ids,
                        'relevance_scores': relevance_scores,
                        'avg_relevance': sum(relevance_scores) / len(relevance_scores) if relevance_scores else 0.0,
                        'papers_count': len(papers)
                    }
                    save_search_history(search_history_item)
                    
                    st.success(results["message"])
                else:
                    st.info("No papers found matching your query.")
                    st.session_state.search_results = []
                    
                    # Save empty search to history
                    search_history_item = {
                        'id': datetime.now().timestamp(),
                        'query': query,
                        'category': category,
                        'categories': [category] if category else [],
                        'timestamp': datetime.now().isoformat(),
                        'paper_ids': [],
                        'relevance_scores': [],
                        'avg_relevance': 0.0,
                        'papers_count': 0
                    }
                    save_search_history(search_history_item)
            else:
                st.error(results["message"])
                st.session_state.search_results = []
        except Exception as e:
            st.error(f"Error during search: {e}")
            st.session_state.search_results = []

@st.cache_resource
def get_api_service():
    return ArxivAPIService()

@st.cache_resource
def get_llm_service():
    return LLMService()

def display_results_modern(api_service):
    """Display search results using modern Streamlit components without HTML."""
    for idx, paper in enumerate(st.session_state.search_results):
        title = paper.get('title', 'N/A')
        relevance_score = paper.get('relevance_score', 0.0)
        authors = paper.get('authors', ['N/A'])
        abstract = paper.get('abstract', 'N/A')
        paper_id = paper.get('id', None)
        category = paper.get('category', 'N/A')
        
        # Create relevance score info
        if relevance_score >= 0.8:
            score_emoji = "🔥"
            score_text = "High"
            score_status = "success"
        elif relevance_score >= 0.6:
            score_emoji = "⭐"
            score_text = "Good"
            score_status = "info"
        elif relevance_score >= 0.4:
            score_emoji = "⚡"
            score_text = "Medium"
            score_status = "warning"
        else:
            score_emoji = "📄"
            score_text = "Low"
            score_status = "error"
        
        # Truncate content for display
        display_title = title if len(title) <= 120 else title[:120] + "..."
        author_str = ', '.join(authors)
        if len(author_str) > 150:
            author_str = author_str[:150] + "..."
        abstract_display = abstract[:400] + ('...' if len(abstract) > 400 else '')
        
        # Clean category and paper_id for display
        category_display = str(category)
        paper_id_display = str(paper_id or 'N/A')
        
        # Create paper card using container
        with st.container():
            # Show relevance indicator
            if score_status == "success":
                st.success(f"{score_emoji} {score_text} Relevance ({relevance_score:.2f})", icon=score_emoji)
            elif score_status == "info":
                st.info(f"{score_emoji} {score_text} Relevance ({relevance_score:.2f})", icon=score_emoji)
            elif score_status == "warning":
                st.warning(f"{score_emoji} {score_text} Relevance ({relevance_score:.2f})", icon=score_emoji)
            else:
                st.error(f"{score_emoji} {score_text} Relevance ({relevance_score:.2f})", icon=score_emoji)
            
            # Title
            st.subheader(display_title)
            
            # Main content in columns
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.markdown(f"**📂 Category:** `{category_display}`")
                st.markdown(f"**👥 Authors:** {author_str}")
                st.markdown("**📄 Abstract:**")
                st.markdown(f"*{abstract_display}*")
            
            with col2:
                st.metric("📊 Relevance", f"{relevance_score:.1%}")
                st.metric("🆔 Paper ID", paper_id_display)
            
            # Action buttons
            st.markdown("---")
            col1, col2, col3 = st.columns([1, 1, 2])
            
            with col1:
                if paper_id and st.button("📥 Download PDF", key=f"dl_{idx}_{paper_id}", type="secondary"):
                    with st.spinner(f"Requesting download for {paper_id}..."):
                        try:
                            download_info = asyncio.run(api_service.download_paper(paper_id))
                            if download_info.get('status') == 'error':
                                st.error(f"Download failed: {download_info.get('message')}")
                            else:
                                st.success(f"Download request sent. {download_info.get('message', '')}")
                        except Exception as e:
                            st.error(f"Failed to request download: {e}")
            
            with col2:
                if st.button("📚 Add to Library", key=f"lib_{idx}_{paper_id}", type="secondary"):
                    st.info("📝 Library feature coming soon!")
            
            with col3:
                if paper_id:
                    arxiv_url = f"https://arxiv.org/abs/{paper_id}"
                    # Use st.link_button if available (Streamlit 1.29+)
                    if hasattr(st, 'link_button'):
                        st.link_button("🌐 View on ArXiv", arxiv_url)
                    else:
                        # Fallback for older versions
                        st.markdown(f"[🌐 View on ArXiv]({arxiv_url})")
            
            # Add divider between papers
            if idx < len(st.session_state.search_results) - 1:
                st.divider()

def display_analytics():
    if "search_results" in st.session_state and st.session_state.search_results:
        results = st.session_state.search_results
        
        # Basic metrics
        total_papers = len(results)
        scores = [p.get('relevance_score', 0.0) for p in results]
        avg_score = sum(scores) / len(scores) if scores else 0
        high_relevance = len([s for s in scores if s >= 0.7])
        
        # Display key metrics
        col1, col2 = st.columns(2)
        with col1:
            st.metric("📄 Total Papers", total_papers)
            st.metric("⭐ Avg Relevance", f"{avg_score:.2f}")
        with col2:
            st.metric("🔥 High Relevance", f"{high_relevance}/{total_papers}")
            success_rate = (high_relevance / total_papers) * 100 if total_papers > 0 else 0
            st.metric("🎯 Success Rate", f"{success_rate:.0f}%")
        
        # Relevance distribution histogram
        if scores:
            fig_hist = px.histogram(
                pd.DataFrame({'Relevance Score': scores}), 
                x='Relevance Score', 
                title="📊 Relevance Score Distribution",
                nbins=10,
                color_discrete_sequence=['#667eea']
            )
            fig_hist.update_layout(
                height=300,
                margin=dict(l=0, r=0, t=40, b=0),
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(size=12)
            )
            st.plotly_chart(fig_hist, use_container_width=True)
    else:
        st.info("📊 No data available for analytics yet.")

def show_history():
    st.header("📚 Search History")
    history = load_search_history()
    
    if not history:
        st.info("No search history found. Your searches will appear here once you start searching!")
        return

    # Sort by timestamp (most recent first)
    history = sorted(history, key=lambda x: x.get('timestamp', ''), reverse=True)
    
    # Add search and filter options
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        search_filter = st.text_input("🔍 Filter by query", placeholder="Search your history...")
    with col2:
        category_filter = st.selectbox("Filter by category", ["All"] + ["cs.AI", "cs.CL", "cs.CV", "cs.LG", "stat.ML", "astro-ph.GA", "cond-mat.mes-hall"])
    with col3:
        if st.button("🗑️ Clear History", type="secondary"):
            history_file = Path(__file__).parent / "data" / "search_history.json"
            try:
                if history_file.exists():
                    history_file.unlink()
                st.success("Search history cleared!")
                st.rerun()
            except Exception as e:
                st.error(f"Error clearing history: {e}")

    # Filter history based on search and category
    filtered_history = history
    if search_filter:
        filtered_history = [h for h in filtered_history if search_filter.lower() in h.get('query', '').lower()]
    if category_filter != "All":
        filtered_history = [h for h in filtered_history if category_filter in h.get('categories', [])]

    if not filtered_history:
        st.info("No history entries match your filters.")
        return

    # Display statistics
    st.markdown("### 📊 Statistics")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Searches", len(filtered_history))
    with col2:
        total_papers = sum(h.get('papers_count', 0) for h in filtered_history)
        st.metric("Total Papers Found", total_papers)
    with col3:
        avg_relevance = sum(h.get('avg_relevance', 0) for h in filtered_history) / len(filtered_history) if filtered_history else 0
        st.metric("Avg Relevance Score", f"{avg_relevance:.2f}")
    with col4:
        successful_searches = len([h for h in filtered_history if h.get('papers_count', 0) > 0])
        success_rate = (successful_searches / len(filtered_history)) * 100 if filtered_history else 0
        st.metric("Success Rate", f"{success_rate:.0f}%")

    st.markdown("### 🕒 Recent Searches")
    
    for i, search_item in enumerate(filtered_history):
        query_display = search_item.get('query', 'N/A')
        timestamp_display = search_item.get('timestamp', 'N/A')
        
        # Parse timestamp for better display
        try:
            dt = datetime.fromisoformat(timestamp_display.replace('Z', '+00:00'))
            time_ago = datetime.now() - dt.replace(tzinfo=None)
            if time_ago.days > 0:
                time_display = f"{time_ago.days} days ago"
            elif time_ago.seconds > 3600:
                time_display = f"{time_ago.seconds // 3600} hours ago"
            else:
                time_display = f"{time_ago.seconds // 60} minutes ago"
        except:
            time_display = timestamp_display

        categories_display = ', '.join(search_item.get('categories', []))
        papers_found_display = search_item.get('papers_count', 0)
        avg_relevance_display = search_item.get('avg_relevance', 0.0)
        search_id = search_item.get('id', datetime.now().timestamp())

        # Create a card using Streamlit components
        with st.container():
            st.subheader(f"🔍 {query_display}")
            
            col1, col2, col3 = st.columns([2, 1, 1])
            with col1:
                st.caption(f"⏰ {time_display}")
                st.write(f"📂 {categories_display or 'All Categories'}")
            with col2:
                st.metric("📄 Papers", papers_found_display)
            with col3:
                st.metric("⭐ Avg Score", f"{avg_relevance_display:.2f}")
            
            col1, col2 = st.columns([1, 1])
            with col1:
                if st.button("🔄 Repeat Search", key=f"repeat_{search_id}", type="primary"):
                    repeat_search(search_item)
                    st.success("Search repeated! Check the results below.")
                    st.rerun()
            with col2:
                if st.button("🗑️ Delete", key=f"delete_{search_id}", type="secondary"):
                    # Remove this item from history
                    updated_history = [h for h in history if h.get('id') != search_id]
                    history_file = Path(__file__).parent / "data" / "search_history.json"
                    try:
                        with open(history_file, "w") as f:
                            json.dump(updated_history, f)
                        st.success("Search deleted!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error deleting search: {e}")
            
            st.divider()

def main():
    # Initialize services
    api = get_api_service()
    llm = get_llm_service()
    
    # Sidebar
    search_type = render_sidebar()
    
    # Main Content Area
    if search_type == "View History":
        show_history()
    else:
        # Add a welcome header
        st.title("🔬 ArXiv Research Assistant")
        st.caption("Discover, analyze, and explore academic papers with AI-powered relevance scoring")
        st.divider()
        
        # Query Input Section
        if search_type == "Natural Language":
            st.markdown("### 🗣️ Natural Language Search")
            st.markdown("Describe what you're looking for in plain English, and we'll find the most relevant papers.")
            
            query = st.text_area(
                "What research are you interested in?", 
                height=120,
                placeholder="E.g.: Recent papers about transformer architectures in computer vision, or quantum computing applications in machine learning...",
                key="nl_query",
                help="Be as specific as possible for better results. You can mention methodologies, applications, or specific domains."
            )
            
            col1, col2 = st.columns([1, 4])
            with col1:
                if st.button("🔍 Search Papers", key="nl_search_button", type="primary") and query:
                    handle_search(api, query)
            with col2:
                if query:
                    st.info(f"💡 Searching for: {query[:100]}{'...' if len(query) > 100 else ''}")
            
        elif search_type == "Category Based":
            st.markdown("### 📂 Category-Based Search")
            st.markdown("Search within specific academic categories for focused results.")
            
            col1, col2 = st.columns([1, 1])
            with col1:
                category_selection = st.selectbox(
                    "🏷️ Academic Category",
                    ["cs.AI", "cs.CL", "cs.CV", "cs.LG", "stat.ML", "astro-ph.GA", "cond-mat.mes-hall"],
                    key="cat_select",
                    help="Select the academic category that best matches your research interest"
                )
            with col2:
                keywords_input = st.text_input(
                    "🔤 Keywords (optional)", 
                    key="cat_keywords",
                    placeholder="Add specific keywords to refine your search...",
                    help="Optional keywords to narrow down results within the selected category"
                )
            
            category_descriptions = {
                "cs.AI": "🤖 Artificial Intelligence - General AI research and applications",
                "cs.CL": "💬 Computational Linguistics - Natural language processing and understanding",
                "cs.CV": "👁️ Computer Vision - Image processing, object recognition, visual analysis",
                "cs.LG": "🧠 Machine Learning - Algorithms, models, and learning systems",
                "stat.ML": "📊 Statistics and Machine Learning - Statistical approaches to ML",
                "astro-ph.GA": "🌌 Astrophysics - Galaxies and cosmology",
                "cond-mat.mes-hall": "⚛️ Condensed Matter Physics - Mesoscopic systems"
            }
            
            if category_selection in category_descriptions:
                st.info(category_descriptions[category_selection])
            
            if st.button("🔍 Search Papers", key="cat_search_button", type="primary") and category_selection:
                handle_search(api, keywords_input, category_selection)

        # Results Section
        st.divider()
        col1, col2 = st.columns([2, 1])
        with col1:
            if "search_results" in st.session_state and st.session_state.search_results:
                st.markdown("### 📄 Search Results")
                st.markdown(f"Found **{len(st.session_state.search_results)}** papers, sorted by relevance:")
                display_results_modern(api)
            else:
                st.markdown("### 📄 Search Results")
                st.info("🔍 Enter a search query above to discover relevant academic papers")

        with col2:
            st.markdown("### 📊 Analytics")
            if "search_results" in st.session_state and st.session_state.search_results:
                display_analytics()
            else:
                st.info("📈 Search results will show analytics here")

if __name__ == "__main__":
    main()
