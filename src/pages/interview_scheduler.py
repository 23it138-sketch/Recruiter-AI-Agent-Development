import streamlit as st
from config import get_data_dir
from utils import load_json
from scheduler import InterviewScheduler

def render_interview_scheduler():
    st.markdown("<h1 class='gradient-text'>📅 Interview Scheduler</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color: #64748B;'>Manage your hiring pipeline and schedule interviews with candidates.</p>", unsafe_allow_html=True)
    
    scheduler = InterviewScheduler()
    
    # Pipeline Stats
    stats = scheduler.get_pipeline_stats()
    
    st.markdown("<div class='section-header'>Pipeline Stats</div>", unsafe_allow_html=True)
    cols = st.columns(5)
    
    stages = [
        ("Applied", "status-applied", "#1976D2", "#E3F2FD"),
        ("Screening", "status-screening", "#F57C00", "#FFF3E0"),
        ("Interview", "status-interview", "#7B1FA2", "#F3E5F5"),
        ("Selected", "status-selected", "#388E3C", "#E8F5E9"),
        ("Rejected", "status-rejected", "#D32F2F", "#FFEBEE")
    ]
    
    for i, (stage, css_class, text_color, bg_color) in enumerate(stages):
        count = stats.get(stage, 0)
        with cols[i]:
            st.markdown(f'''
            <div style="background: {bg_color}; padding: 16px; border-radius: 12px; text-align: center; border: 1px solid {text_color}40;">
                <div style="font-size: 2rem; font-weight: 700; color: {text_color};">{count}</div>
                <div style="font-weight: 600; color: {text_color};">{stage}</div>
            </div>
            ''', unsafe_allow_html=True)
            
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["📝 Schedule Interview", "📋 All Interviews"])
    
    with tab1:
        st.markdown("### Schedule New Interview")
        
        # Load jobs
        jobs_file = get_data_dir() / "sample_jobs.json"
        jobs = load_json(jobs_file) if jobs_file.exists() else []
        job_titles = [j.get("title") for j in jobs] if jobs else ["No jobs available"]
        
        default_candidate = ""
        if st.session_state.get("parsed_resume"):
            default_candidate = st.session_state.parsed_resume.name
            
        with st.form("schedule_form"):
            col1, col2 = st.columns(2)
            with col1:
                candidate_name = st.text_input("Candidate Name", value=default_candidate)
                job_title = st.selectbox("Job Role", options=job_titles)
            with col2:
                import datetime
                date = st.date_input("Interview Date", min_value=datetime.date.today())
                date_str = date.strftime("%Y-%m-%d")
                slots = scheduler.suggest_slots(date_str)
                time_slot = st.selectbox("Time Slot", options=slots)
                
            notes = st.text_area("Notes (Optional)")
            
            submitted = st.form_submit_button("Schedule Interview", type="primary")
            if submitted:
                if not candidate_name or not job_title or "No jobs" in job_title:
                    st.error("Please provide candidate name and valid job role.")
                else:
                    new_interview = scheduler.create_interview(candidate_name, job_title, date_str, time_slot, notes)
                    st.success(f"Interview scheduled for {candidate_name} on {date_str} at {time_slot}!")
                    
    with tab2:
        interviews = scheduler.get_all_interviews()
        
        if not interviews:
            st.markdown('''
            <div class="empty-state">
                <h3 style="color: #64748B;">No Interviews Scheduled</h3>
                <p>Use the "Schedule Interview" tab to add candidates to the pipeline.</p>
            </div>
            ''', unsafe_allow_html=True)
        else:
            for inv in reversed(interviews):
                status_class = f"status-{inv.status.lower()}"
                
                with st.container():
                    st.markdown(f'''
                    <div class="card" style="padding: 16px; margin-bottom: 12px; border-left: 4px solid var(--primary);">
                        <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                            <div>
                                <h4 style="margin: 0;">{inv.candidate_name}</h4>
                                <p style="margin: 4px 0; color: #64748B;">{inv.job_title}</p>
                                <p style="margin: 4px 0; font-size: 0.9rem;"><strong>📅 {inv.date}</strong> | ⏰ {inv.time_slot}</p>
                            </div>
                            <div>
                                <span class="status-badge {status_class}">{inv.status}</span>
                            </div>
                        </div>
                    </div>
                    ''', unsafe_allow_html=True)
                    
                    # Actions
                    col_a, col_b, col_c = st.columns([2, 1, 1])
                    with col_a:
                        new_status = st.selectbox(
                            "Update Status", 
                            ["Applied", "Screening", "Interview", "Selected", "Rejected"],
                            index=["Applied", "Screening", "Interview", "Selected", "Rejected"].index(inv.status),
                            key=f"status_{inv.id}"
                        )
                        if new_status != inv.status:
                            if st.button("Save Status", key=f"btn_status_{inv.id}"):
                                scheduler.update_status(inv.id, new_status)
                                st.rerun()
                                
                    with col_c:
                        if st.button("🗑️ Delete", key=f"del_{inv.id}"):
                            scheduler.delete_interview(inv.id)
                            st.rerun()
                    
                    st.markdown("<hr style='margin: 10px 0; border-color: #eee;'>", unsafe_allow_html=True)
