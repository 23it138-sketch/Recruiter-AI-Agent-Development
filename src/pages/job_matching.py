import streamlit as st
from config import get_data_dir
from utils import load_json
from job_matcher import JobMatcher

def render_job_matching():
    st.markdown("<h1 class='gradient-text'>🎯 Job Matching</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color: #64748B;'>Match the current candidate against active job listings using AI-driven scoring.</p>", unsafe_allow_html=True)
    
    if not st.session_state.get("parsed_resume"):
        st.markdown('''
        <div class="empty-state">
            <h2 style="color: #64748B;">No Candidate Selected</h2>
            <p>Please upload or parse a resume in the <strong>Resume Screening</strong> page first.</p>
        </div>
        ''', unsafe_allow_html=True)
        return
        
    candidate = st.session_state.parsed_resume
    st.markdown(f'''
    <div class="info-card">
        <strong>Current Candidate:</strong> {candidate.name} | <strong>Total Skills:</strong> {len(candidate.skills)}
    </div>
    ''', unsafe_allow_html=True)
    
    jobs_file = get_data_dir() / "sample_jobs.json"
    if not jobs_file.exists():
        st.error("Sample jobs file not found!")
        return
        
    jobs = load_json(jobs_file)
    if not jobs:
        st.error("No jobs loaded.")
        return
        
    matcher = JobMatcher()
    
    col1, col2 = st.columns([1, 3])
    with col1:
        min_score = st.slider("Minimum Match Score (%)", 0, 100, 50)
        
    if st.button("Run AI Match Analysis", type="primary"):
        with st.spinner("Analyzing candidate fit for all roles..."):
            matches = matcher.match_all_jobs(candidate, jobs)
            # Filter and sort
            filtered_matches = [(j, r) for j, r in matches if r.score >= min_score]
            st.session_state.job_matches = filtered_matches
            
    matches_to_display = st.session_state.get("job_matches")
    
    if matches_to_display is not None:
        st.markdown(f"<div class='section-header'>Top Matches ({len(matches_to_display)})</div>", unsafe_allow_html=True)
        
        if not matches_to_display:
            st.warning("No jobs met the minimum score threshold.")
        else:
            for job, result in matches_to_display:
                score_class = "match-score-high" if result.score >= 80 else "match-score-medium" if result.score >= 60 else "match-score-low"
                
                # HTML Card
                st.markdown(f'''
                <div class="card">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <h3 style="margin: 0; color: var(--dark);">{job.get("title", "Unknown")}</h3>
                            <p style="margin: 4px 0; color: #64748B;">🏢 {job.get("company")} | 📍 {job.get("location")} | 💰 {job.get("salary_range", "")}</p>
                        </div>
                        <div class="match-score-container">
                            <div class="match-score {score_class}">{result.score:.0f}%</div>
                            <div style="font-size: 0.8rem; color: #64748B; font-weight: bold;">OVERALL MATCH</div>
                        </div>
                    </div>
                    
                    <div style="display: flex; gap: 20px; margin-top: 16px; margin-bottom: 16px;">
                        <div style="flex: 1;">
                            <div style="display: flex; justify-content: space-between; font-size: 0.85rem; margin-bottom: 4px;">
                                <span>Skills Fit</span><span>{result.skill_score:.0f}%</span>
                            </div>
                            <div style="height: 6px; background: #eee; border-radius: 3px;">
                                <div style="height: 100%; width: {result.skill_score}%; background: var(--primary); border-radius: 3px;"></div>
                            </div>
                        </div>
                        <div style="flex: 1;">
                            <div style="display: flex; justify-content: space-between; font-size: 0.85rem; margin-bottom: 4px;">
                                <span>Experience</span><span>{result.experience_score:.0f}%</span>
                            </div>
                            <div style="height: 6px; background: #eee; border-radius: 3px;">
                                <div style="height: 100%; width: {result.experience_score}%; background: var(--secondary); border-radius: 3px;"></div>
                            </div>
                        </div>
                        <div style="flex: 1;">
                            <div style="display: flex; justify-content: space-between; font-size: 0.85rem; margin-bottom: 4px;">
                                <span>Education</span><span>{result.education_score:.0f}%</span>
                            </div>
                            <div style="height: 6px; background: #eee; border-radius: 3px;">
                                <div style="height: 100%; width: {result.education_score}%; background: #00B894; border-radius: 3px;"></div>
                            </div>
                        </div>
                    </div>
                </div>
                ''', unsafe_allow_html=True)
                
                # Skills Display
                matched_html = " ".join([f'<span class="skill-badge skill-badge-matched">✓ {s}</span>' for s in result.matched_skills])
                missing_html = " ".join([f'<span class="skill-badge skill-badge-missing">✕ {s}</span>' for s in result.missing_skills])
                
                st.markdown(f"**Matched Skills:**<br>{matched_html if matched_html else 'None'}", unsafe_allow_html=True)
                st.markdown(f"**Missing Skills:**<br>{missing_html if missing_html else 'None'}", unsafe_allow_html=True)
                
                with st.expander("Detailed AI Analysis"):
                    col_a, col_b = st.columns(2)
                    with col_a:
                        st.markdown("#### ✅ Strengths")
                        for s in result.strengths:
                            st.markdown(f"- {s}")
                    with col_b:
                        st.markdown("#### ⚠️ Potential Weaknesses")
                        for w in result.weaknesses:
                            st.markdown(f"- {w}")
                            
                    st.markdown("#### 💡 Recommendation")
                    st.info(result.recommendation)
                    
                st.markdown("<hr style='margin: 30px 0;'>", unsafe_allow_html=True)
