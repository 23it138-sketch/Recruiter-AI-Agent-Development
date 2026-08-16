import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

import streamlit as st
from config import APP_NAME, APP_VERSION, is_gemini_available
from pages.dashboard import render_dashboard
from pages.resume_screening import render_resume_screening
from pages.job_matching import render_job_matching
from pages.interview_scheduler import render_interview_scheduler
from pages.ai_assistant import render_ai_assistant

# Page config must be first
st.set_page_config(
    page_title=APP_NAME,
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

def inject_css():
    css = """
    <style>
    /* Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    /* General Settings */
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    /* Primary / Secondary colors used in gradients */
    :root {
        --primary: #4A90D9;
        --secondary: #6C5CE7;
        --success: #00B894;
        --warning: #FDCB6E;
        --danger: #E17055;
        --dark: #2D3436;
        --light: #F0F4F8;
    }

    /* Metric Cards */
    .metric-card {
        background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%);
        border-radius: 12px;
        padding: 24px;
        color: white;
        box-shadow: 0 10px 20px rgba(74, 144, 217, 0.2);
        margin-bottom: 20px;
        transition: transform 0.2s ease;
    }
    .metric-card:hover {
        transform: translateY(-5px);
    }
    .metric-label {
        font-size: 1.1rem;
        font-weight: 500;
        opacity: 0.9;
        margin-bottom: 8px;
    }
    .metric-value {
        font-size: 2.5rem;
        font-weight: 700;
    }
    
    /* Generic Card */
    .card {
        background: white;
        border-radius: 12px;
        padding: 24px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        border: 1px solid rgba(0,0,0,0.05);
        margin-bottom: 24px;
    }
    
    /* Skill Badges */
    .skill-badge {
        display: inline-block;
        padding: 6px 14px;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
        margin: 4px;
        color: white;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .skill-badge-matched { background: linear-gradient(135deg, #00B894, #00CEC9); }
    .skill-badge-missing { background: linear-gradient(135deg, #E17055, #D63031); }
    .skill-badge-category-1 { background: #74B9FF; color: #1e3799; }
    .skill-badge-category-2 { background: #A29BFE; color: #3c0c59; }
    .skill-badge-category-3 { background: #55EFC4; color: #006266; }
    .skill-badge-category-4 { background: #FFEAA7; color: #d35400; }
    .skill-badge-category-5 { background: #FAB1A0; color: #b71540; }
    .skill-badge-default { background: #DFE6E9; color: #2D3436; }

    /* Match Scores */
    .match-score-container {
        text-align: center;
        padding: 16px;
    }
    .match-score {
        font-size: 3rem;
        font-weight: 700;
        margin-bottom: 8px;
    }
    .match-score-high { color: var(--success); }
    .match-score-medium { color: var(--warning); }
    .match-score-low { color: var(--danger); }
    
    /* Status Badges */
    .status-badge {
        display: inline-flex;
        align-items: center;
        padding: 6px 12px;
        border-radius: 12px;
        font-size: 0.85rem;
        font-weight: 600;
    }
    .status-badge::before {
        content: '';
        display: inline-block;
        width: 8px;
        height: 8px;
        border-radius: 50%;
        margin-right: 8px;
    }
    .status-applied { background: #E3F2FD; color: #1976D2; }
    .status-applied::before { background: #1976D2; }
    .status-screening { background: #FFF3E0; color: #F57C00; }
    .status-screening::before { background: #F57C00; }
    .status-interview { background: #F3E5F5; color: #7B1FA2; }
    .status-interview::before { background: #7B1FA2; }
    .status-selected { background: #E8F5E9; color: #388E3C; }
    .status-selected::before { background: #388E3C; }
    .status-rejected { background: #FFEBEE; color: #D32F2F; }
    .status-rejected::before { background: #D32F2F; }
    
    /* Text Styles */
    .gradient-text {
        background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 700;
    }
    .section-header {
        font-size: 1.5rem;
        font-weight: 600;
        margin-bottom: 16px;
        color: var(--dark);
        border-bottom: 2px solid var(--light);
        padding-bottom: 8px;
    }
    
    /* Layout/Misc */
    .empty-state {
        text-align: center;
        padding: 40px 20px;
        background: #F8FAFC;
        border-radius: 12px;
        border: 2px dashed #CBD5E1;
        color: #64748B;
    }
    .info-card {
        background: #F0F4F8;
        border-left: 4px solid var(--primary);
        padding: 16px;
        border-radius: 0 8px 8px 0;
        margin-bottom: 20px;
    }
    
    /* Buttons Override */
    .stButton>button {
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.2s;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

def init_session_state():
    if "parsed_resume" not in st.session_state:
        st.session_state.parsed_resume = None
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "selected_job" not in st.session_state:
        st.session_state.selected_job = None
    if "job_matches" not in st.session_state:
        st.session_state.job_matches = None

def main():
    inject_css()
    init_session_state()
    
    # Sidebar
    st.sidebar.markdown(f"## 🎯 <span class='gradient-text'>{APP_NAME}</span>", unsafe_allow_html=True)
    st.sidebar.markdown("---")
    
    page = st.sidebar.radio(
        "Navigation",
        ["📊 Dashboard", "📄 Resume Screening", "🎯 Job Matching", "📅 Interview Scheduler", "🤖 AI Assistant"]
    )
    
    st.sidebar.markdown("---")
    if is_gemini_available():
        st.sidebar.markdown("🟢 **Gemini AI:** Connected")
    else:
        st.sidebar.markdown("🔴 **Gemini AI:** Disconnected")
        
    st.sidebar.markdown(f"<small style='color: #888;'>Version {APP_VERSION}</small>", unsafe_allow_html=True)
    
    # Routing
    if page == "📊 Dashboard":
        render_dashboard()
    elif page == "📄 Resume Screening":
        render_resume_screening()
    elif page == "🎯 Job Matching":
        render_job_matching()
    elif page == "📅 Interview Scheduler":
        render_interview_scheduler()
    elif page == "🤖 AI Assistant":
        render_ai_assistant()

if __name__ == "__main__":
    main()
