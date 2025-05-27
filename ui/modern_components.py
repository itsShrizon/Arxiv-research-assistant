# modern_components.py

import streamlit as st
from typing import Dict, Any, Optional, List

def render_relevance_badge(score: float, score_text: str) -> None:
    """
    Render a relevance score badge using Streamlit's built-in styling.
    Modern approach that doesn't rely on HTML.
    """
    # Determine color scheme based on score
    if score >= 0.8:
        delta_color = "normal"
        emoji = "🔥"
    elif score >= 0.6:
        delta_color = "normal"
        emoji = "⭐"
    elif score >= 0.4:
        delta_color = "off"
        emoji = "⚡"
    else:
        delta_color = "off"
        emoji = "📄"
    
    # Use metric with custom styling
    st.metric(
        label=f"{emoji} Relevance",
        value=score_text,
        delta=f"{score:.2f}",
        delta_color=delta_color
    )

def render_paper_card_modern(paper: Dict[str, Any], idx: int, api_service) -> None:
    """
    Render a paper card using modern Streamlit components.
    No HTML required - uses native Streamlit styling.
    """
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
    elif relevance_score >= 0.6:
        score_emoji = "⭐"
        score_text = "Good"
    elif relevance_score >= 0.4:
        score_emoji = "⚡"
        score_text = "Medium"
    else:
        score_emoji = "📄"
        score_text = "Low"
    
    # Truncate content for display
    display_title = title if len(title) <= 120 else title[:120] + "..."
    author_str = ', '.join(authors)
    if len(author_str) > 150:
        author_str = author_str[:150] + "..."
    abstract_display = abstract[:400] + ('...' if len(abstract) > 400 else '')
    
    # Clean category and paper_id for display
    category_display = str(category)
    paper_id_display = str(paper_id or 'N/A')
    
    # Create paper card using container and columns
    with st.container():
        # Use a colored border to indicate relevance
        if relevance_score >= 0.8:
            st.success("", icon=score_emoji)
        elif relevance_score >= 0.6:
            st.info("", icon=score_emoji)
        elif relevance_score >= 0.4:
            st.warning("", icon=score_emoji)
        else:
            st.error("", icon=score_emoji)
        
        # Title and basic info
        st.subheader(f"{score_emoji} {display_title}")
        
        # Main content in columns
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.markdown(f"**📂 Category:** `{category_display}`")
            st.markdown(f"**👥 Authors:** {author_str}")
            st.markdown("**📄 Abstract:**")
            st.markdown(f"*{abstract_display}*")
        
        with col2:
            render_relevance_badge(relevance_score, score_text)
            st.metric("🆔 Paper ID", paper_id_display)
        
        # Action buttons
        st.markdown("---")
        col1, col2, col3 = st.columns([1, 1, 2])
        
        with col1:
            if paper_id and st.button("📥 Download PDF", key=f"dl_{idx}_{paper_id}", type="secondary"):
                with st.spinner(f"Requesting download for {paper_id}..."):
                    try:
                        import asyncio
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

def render_score_indicator(score: float) -> None:
    """
    Render a visual score indicator using progress bar.
    """
    if score >= 0.8:
        st.success(f"🔥 High Relevance: {score:.1%}")
    elif score >= 0.6:
        st.info(f"⭐ Good Relevance: {score:.1%}")
    elif score >= 0.4:
        st.warning(f"⚡ Medium Relevance: {score:.1%}")
    else:
        st.error(f"📄 Low Relevance: {score:.1%}")
    
    # Add progress bar
    st.progress(score)

def render_styled_header(title: str, subtitle: str = None) -> None:
    """
    Render a styled header without HTML.
    """
    st.title(f"🔬 {title}")
    if subtitle:
        st.caption(subtitle)
    st.divider()

def render_info_card(title: str, content: str, icon: str = "ℹ️") -> None:
    """
    Render an information card using Streamlit's info component.
    """
    st.info(f"{icon} **{title}**\n\n{content}")

def render_search_stats(results: List[Dict[str, Any]]) -> None:
    """
    Render search statistics using metrics.
    """
    if not results:
        st.warning("No results to analyze")
        return
    
    total_papers = len(results)
    scores = [p.get('relevance_score', 0.0) for p in results]
    avg_score = sum(scores) / len(scores) if scores else 0
    high_relevance = len([s for s in scores if s >= 0.7])
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("📄 Total Papers", total_papers)
    
    with col2:
        st.metric("⭐ Avg Relevance", f"{avg_score:.2f}")
    
    with col3:
        st.metric("🔥 High Relevance", f"{high_relevance}/{total_papers}")

def render_category_badge(category: str) -> str:
    """
    Return a styled category string with emojis.
    """
    category_emojis = {
        "cs.AI": "🤖",
        "cs.CL": "💬", 
        "cs.CV": "👁️",
        "cs.LG": "🧠",
        "stat.ML": "📊",
        "astro-ph.GA": "🌌",
        "cond-mat.mes-hall": "⚛️"
    }
    
    emoji = category_emojis.get(category, "📂")
    return f"{emoji} {category}"
