import streamlit as st
from pathlib import Path
from config import is_gemini_available, GEMINI_MODEL, get_data_dir
from utils import load_json
from scheduler import InterviewScheduler

def render_dashboard():
    st.markdown("<h1 class='gradient-text'>Welcome to Recruiter AI Agent</h1>", unsafe_allow_html=True)
    st.markdown("<p style='font-size: 1.2rem; color: #64748B;'>Streamline your hiring process with AI-powered resume screening, job matching, and interview scheduling.</p>", unsafe_allow_html=True)
    
    # Collect Metrics
    total_resumes = 1 if st.session_state.parsed_resume else 0
    
    jobs_file = get_data_dir() / "sample_jobs.json"
    jobs = load_json(jobs_file) if jobs_file.exists() else []
    active_jobs = len(jobs)
    
    scheduler = InterviewScheduler()
    interviews = scheduler.get_all_interviews()
    total_interviews = len(interviews)
    
    avg_match_score = "N/A"
    if st.session_state.get("job_matches"):
        scores = [result.score for _, result in st.session_state.job_matches]
        if scores:
            avg_match_score = f"{sum(scores)/len(scores):.1f}%"
            
    # Metrics Row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f'''
        <div class="metric-card">
            <div class="metric-label">📄 Resumes Processed</div>
            <div class="metric-value">{total_resumes}</div>
        </div>
        ''', unsafe_allow_html=True)
        
    with col2:
        st.markdown(f'''
        <div class="metric-card" style="background: linear-gradient(135deg, #00B894 0%, #00CEC9 100%);">
            <div class="metric-label">💼 Active Job Listings</div>
            <div class="metric-value">{active_jobs}</div>
        </div>
        ''', unsafe_allow_html=True)
        
    with col3:
        st.markdown(f'''
        <div class="metric-card" style="background: linear-gradient(135deg, #FDCB6E 0%, #E17055 100%);">
            <div class="metric-label">📅 Interviews Scheduled</div>
            <div class="metric-value">{total_interviews}</div>
        </div>
        ''', unsafe_allow_html=True)
        
    with col4:
        st.markdown(f'''
        <div class="metric-card" style="background: linear-gradient(135deg, #6C5CE7 0%, #A29BFE 100%);">
            <div class="metric-label">🎯 Avg Match Score</div>
            <div class="metric-value">{avg_match_score}</div>
        </div>
        ''', unsafe_allow_html=True)
        
    # Layout below
    col_left, col_right = st.columns([2, 1])
    
    with col_left:
        st.markdown("<div class='section-header'>🚀 Quick Actions</div>", unsafe_allow_html=True)
        st.info("Use the sidebar navigation to switch between different workflows.")
        
        st.markdown("<div class='section-header'>💼 Job Listings Preview</div>", unsafe_allow_html=True)
        if jobs:
            for job in jobs[:5]:
                st.markdown(f'''
                <div class="card" style="padding: 16px; margin-bottom: 12px;">
                    <h4 style="margin: 0; color: #2D3436;">{job.get("title", "Unknown Role")}</h4>
                    <p style="margin: 4px 0 0 0; color: #64748B; font-size: 0.9rem;">
                        🏢 {job.get("company", "Company")} | 📍 {job.get("location", "Location")}
                    </p>
                </div>
                ''', unsafe_allow_html=True)
        else:
            st.markdown("<div class='empty-state'>No job listings found.</div>", unsafe_allow_html=True)

    with col_right:
        st.markdown("<div class='section-header'>🤖 AI Status</div>", unsafe_allow_html=True)
        if is_gemini_available():
            st.markdown(f'''
            <div class="card" style="border-top: 4px solid #00B894;">
                <h3 style="color: #00B894; margin-top: 0;">✅ Connected</h3>
                <p><strong>Model:</strong> {GEMINI_MODEL}</p>
                <hr style="border-color: #eee;">
                <p style="font-size: 0.9rem;">Features enabled:</p>
                <ul style="font-size: 0.9rem; padding-left: 20px;">
                    <li>Semantic resume parsing</li>
                    <li>Context-aware skill extraction</li>
                    <li>Advanced job matching</li>
                    <li>Interactive AI assistant</li>
                </ul>
            </div>
            ''', unsafe_allow_html=True)
        else:
            st.markdown(f'''
            <div class="card" style="border-top: 4px solid #E17055;">
                <h3 style="color: #E17055; margin-top: 0;">❌ Disconnected</h3>
                <p>Gemini API is not configured properly.</p>
                <hr style="border-color: #eee;">
                <p style="font-size: 0.9rem;">Please check your .env file and ensure GEMINI_API_KEY is set.</p>
            </div>
            ''', unsafe_allow_html=True)
            
        st.markdown("<div class='section-header'>📊 Pipeline Overview</div>", unsafe_allow_html=True)
        stats = scheduler.get_pipeline_stats()
        if sum(stats.values()) > 0:
            for stage, count in stats.items():
                st.markdown(f'''
                <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                    <span>{stage}</span>
                    <strong>{count}</strong>
                </div>
                ''', unsafe_allow_html=True)
        else:
            st.markdown("<div class='empty-state' style='padding: 20px;'>No candidates in pipeline yet.</div>", unsafe_allow_html=True)

    st.markdown("<div class='section-header' style='margin-top: 30px;'>📖 Getting Started</div>", unsafe_allow_html=True)
    st.markdown("""
    1. **Upload a Resume**: Go to **Resume Screening** to upload or paste a candidate's resume. The AI will extract their skills and experience.
    2. **Match with Jobs**: Navigate to **Job Matching** to see how well the candidate fits your open positions.
    3. **Schedule Interview**: Use the **Interview Scheduler** to manage your pipeline and set up interviews.
    4. **Ask the AI**: Need help summarizing a profile or writing interview questions? Check out the **AI Assistant**.
    """)
