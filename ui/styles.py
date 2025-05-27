# styles.py

# Complete CSS styles for the ArXiv MCP Server UI
# Updated for modern Streamlit compatibility
main_css = """
<style>
/* Import Google Fonts */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

/* Global Styling */
.main {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    font-family: 'Inter', sans-serif;
}

/* Content container with glassmorphism */
.block-container {
    background: rgba(255, 255, 255, 0.95);
    backdrop-filter: blur(10px);
    border-radius: 20px;
    padding: 2rem;
    margin-top: 1rem;
    box-shadow: 0 8px 32px rgba(31, 38, 135, 0.37);
    border: 1px solid rgba(255, 255, 255, 0.18);
}

/* Sidebar styling */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
}

[data-testid="stSidebar"] > div {
    color: white;
}

[data-testid="stSidebar"] .stMarkdown {
    color: white;
}

/* Enhanced Button styling - target Streamlit's button classes */
.stButton > button {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 0.5rem 1.5rem !important;
    font-weight: 500 !important;
    transition: all 0.3s ease !important;
    box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3) !important;
    font-family: 'Inter', sans-serif !important;
}

.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4) !important;
}

.stButton > button:active {
    transform: translateY(0) !important;
    box-shadow: 0 2px 10px rgba(102, 126, 234, 0.2) !important;
}

/* Link button styling */
.stLinkButton > a {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 0.5rem 1.5rem !important;
    font-weight: 500 !important;
    transition: all 0.3s ease !important;
    box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3) !important;
    font-family: 'Inter', sans-serif !important;
    text-decoration: none !important;
}

.stLinkButton > a:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4) !important;
    color: white !important;
}

/* Secondary button styling */
button[data-baseweb="button"][kind="secondary"] {
    background: linear-gradient(135deg, #e2e8f0 0%, #cbd5e0 100%) !important;
    color: #4a5568 !important;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1) !important;
}

button[data-baseweb="button"][kind="secondary"]:hover {
    background: linear-gradient(135deg, #cbd5e0 0%, #a0aec0 100%) !important;
    color: #2d3748 !important;
}

/* Input styling */
.stTextArea textarea, .stTextInput input, .stSelectbox select {
    border-radius: 10px !important;
    border: 2px solid #e2e8f0 !important;
    padding: 12px !important;
    transition: all 0.3s ease !important;
    font-family: 'Inter', sans-serif !important;
}

.stTextArea textarea:focus, .stTextInput input:focus, .stSelectbox select:focus {
    border-color: #667eea !important;
    box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1) !important;
}

/* Metrics styling */
[data-testid="metric-container"] {
    background: linear-gradient(145deg, #ffffff 0%, #f8f9ff 100%) !important;
    border-radius: 12px !important;
    padding: 1rem !important;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05) !important;
    border: 1px solid rgba(102, 126, 234, 0.1) !important;
}

/* Container styling for paper cards */
.stContainer {
    background: linear-gradient(145deg, #ffffff 0%, #f8f9ff 100%);
    border-radius: 16px;
    padding: 20px;
    margin-bottom: 20px;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
    border: 1px solid rgba(255, 255, 255, 0.2);
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

/* Expander styling */
.streamlit-expanderHeader {
    background: linear-gradient(145deg, #ffffff 0%, #f8f9ff 100%) !important;
    border-radius: 12px !important;
    border: 1px solid rgba(102, 126, 234, 0.1) !important;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05) !important;
}

.streamlit-expanderContent {
    background: linear-gradient(145deg, #ffffff 0%, #f8f9ff 100%) !important;
    border-radius: 0 0 12px 12px !important;
    padding: 20px !important;
}

/* Success/Error message styling */
.stSuccess {
    background: linear-gradient(145deg, #d4edda 0%, #c3e6cb 100%) !important;
    border-radius: 10px !important;
    border-left: 4px solid #28a745 !important;
}

.stError {
    background: linear-gradient(145deg, #f8d7da 0%, #f5c6cb 100%) !important;
    border-radius: 10px !important;
    border-left: 4px solid #dc3545 !important;
}

.stInfo {
    background: linear-gradient(145deg, #d1ecf1 0%, #bee5eb 100%) !important;
    border-radius: 10px !important;
    border-left: 4px solid #17a2b8 !important;
}

.stWarning {
    background: linear-gradient(145deg, #fff3cd 0%, #ffeaa7 100%) !important;
    border-radius: 10px !important;
    border-left: 4px solid #ffc107 !important;
}

/* Header styling */
h1, h2, h3, h4, h5, h6 {
    color: #2d3748 !important;
    font-weight: 600 !important;
    font-family: 'Inter', sans-serif !important;
}

/* Progress bar styling */
.stProgress > div > div {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
}

/* Loading spinner customization */
.stSpinner > div {
    border-top-color: #667eea !important;
}

/* Divider styling */
hr {
    border: none !important;
    height: 2px !important;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
    border-radius: 2px !important;
    margin: 2rem 0 !important;
}

/* Hide Streamlit branding */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
.stDeployButton {display: none;}

/* Code block styling */
.stCode {
    background: linear-gradient(145deg, #f8f9ff 0%, #e6f3ff 100%) !important;
    border-radius: 8px !important;
    border: 1px solid rgba(102, 126, 234, 0.1) !important;
}

/* Caption styling */
.stCaption {
    color: #718096 !important;
    font-style: italic !important;
}

/* Markdown link styling */
.stMarkdown a {
    color: #667eea !important;
    text-decoration: none !important;
    font-weight: 500 !important;
}

.stMarkdown a:hover {
    color: #764ba2 !important;
    text-decoration: underline !important;
}
</style>
"""

# Legacy custom button CSS for backwards compatibility
custom_button_css = """
<style>
.custom-button {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 12px 24px;
    border: none;
    border-radius: 8px;
    font-size: 16px;
    font-weight: 500;
    cursor: pointer;
    display: inline-block;
    text-align: center;
    text-decoration: none;
    transition: all 0.3s ease;
    box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    font-family: 'Inter', sans-serif;
}

.custom-button:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
    text-decoration: none;
    color: white;
}

.custom-button:active {
    transform: translateY(0);
    box-shadow: 0 2px 10px rgba(102, 126, 234, 0.2);
}
</style>
"""

# Utility functions for applying custom styling
def apply_custom_button_style(button_html: str, button_class: str = "custom-button") -> str:
    """
    Apply custom styling to button HTML.
    
    Args:
        button_html: The HTML content for the button
        button_class: CSS class to apply (default: "custom-button")
    
    Returns:
        Styled button HTML
    """
    return f'<div class="{button_class}">{button_html}</div>'

def get_styled_button_html(text: str, onclick: str = "", button_id: str = "", button_class: str = "custom-button") -> str:
    """
    Generate styled button HTML.
    
    Args:
        text: Button text
        onclick: JavaScript onclick handler
        button_id: Button ID attribute
        button_class: CSS class to apply
    
    Returns:
        Complete styled button HTML
    """
    id_attr = f'id="{button_id}"' if button_id else ""
    onclick_attr = f'onclick="{onclick}"' if onclick else ""
    
    return f'''
    <button class="{button_class}" {id_attr} {onclick_attr}>
        {text}
    </button>
    '''

# Color scheme variables for consistency
COLORS = {
    "primary_gradient": "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
    "secondary_gradient": "linear-gradient(135deg, #e2e8f0 0%, #cbd5e0 100%)",
    "success_gradient": "linear-gradient(145deg, #d4edda 0%, #c3e6cb 100%)",
    "error_gradient": "linear-gradient(145deg, #f8d7da 0%, #f5c6cb 100%)",
    "info_gradient": "linear-gradient(145deg, #d1ecf1 0%, #bee5eb 100%)",
    "card_gradient": "linear-gradient(145deg, #ffffff 0%, #f8f9ff 100%)",
    "primary_color": "#667eea",
    "secondary_color": "#764ba2",
    "text_primary": "#2d3748",
    "text_secondary": "#4a5568",
    "text_muted": "#718096"
}
