import streamlit as st
import os
from config import get_data_dir
from resume_parser import ResumeParser
from skill_extractor import SkillExtractor

def render_resume_screening():
    st.markdown("<h1 class='gradient-text'>📄 Resume Screening</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color: #64748B;'>Upload a candidate's resume to automatically extract structured data and skills using AI.</p>", unsafe_allow_html=True)
    
    parser = ResumeParser()
    extractor = SkillExtractor()
    
    tab1, tab2, tab3 = st.tabs(["📁 Upload File", "📝 Paste Text", "📚 Sample Resumes"])
    
    resume_text = None
    
    with tab1:
        uploaded_file = st.file_uploader("Upload candidate resume (PDF or TXT)", type=['pdf', 'txt'])
        if uploaded_file:
            with st.spinner("Extracting text from document..."):
                if uploaded_file.name.endswith('.pdf'):
                    resume_text = parser.parse_pdf(uploaded_file)
                else:
                    resume_text = parser.parse_txt(uploaded_file.getvalue())
                    
    with tab2:
        pasted_text = st.text_area("Paste resume content here", height=200)
        if st.button("Process Pasted Text", type="primary") and pasted_text:
            resume_text = pasted_text
            
    with tab3:
        samples_dir = get_data_dir() / "sample_resumes"
        if samples_dir.exists():
            sample_files = list(samples_dir.glob("*.txt"))
            if sample_files:
                st.info("Select a sample resume below to test the parsing pipeline.")
                for sample in sample_files:
                    if st.button(f"Load {sample.name}"):
                        with st.spinner("Loading sample..."):
                            resume_text = parser.parse_txt(sample.read_bytes())
            else:
                st.warning("No sample resumes found in data/sample_resumes/")
        else:
            st.warning("Sample resumes directory not found.")
            
    if resume_text:
        with st.spinner("AI is analyzing the resume..."):
            try:
                candidate = parser.extract_info(resume_text)
                st.session_state.parsed_resume = candidate
                st.success("Resume processed successfully!")
            except Exception as e:
                st.error(f"Error parsing resume: {str(e)}")
                
    if st.session_state.parsed_resume:
        candidate = st.session_state.parsed_resume
        st.markdown("<hr>", unsafe_allow_html=True)
        
        col1, col2 = st.columns([3, 2])
        
        with col1:
            st.markdown("<div class='section-header'>👤 Candidate Profile</div>", unsafe_allow_html=True)
            st.markdown(f'''
            <div class="card">
                <h2 style="margin-top: 0; color: #2D3436;">{candidate.name}</h2>
                <p style="color: #64748B;">
                    📧 {candidate.email} &nbsp;|&nbsp; 📱 {candidate.phone}
                </p>
                
                <h4 style="margin-top: 20px;">Summary</h4>
                <p>{candidate.summary}</p>
            </div>
            ''', unsafe_allow_html=True)
            
            if candidate.experience:
                st.markdown("#### 💼 Experience")
                for exp in candidate.experience:
                    st.markdown(f"- {exp}")
            
            if candidate.education:
                st.markdown("#### 🎓 Education")
                for edu in candidate.education:
                    st.markdown(f"- {edu}")
                    
        with col2:
            st.markdown("<div class='section-header'>🎯 Skills Analysis</div>", unsafe_allow_html=True)
            
            skills_dict = extractor.categorize(candidate.skills)
            
            st.markdown(f'''
            <div class="card" style="text-align: center; margin-bottom: 20px;">
                <div style="font-size: 3rem; font-weight: bold; color: var(--primary);">{len(candidate.skills)}</div>
                <div style="color: #64748B; font-weight: 500;">Total Skills Extracted</div>
            </div>
            ''', unsafe_allow_html=True)
            
            st.markdown('<div class="card">', unsafe_allow_html=True)
            for i, (cat, cat_skills) in enumerate(skills_dict.items()):
                if cat_skills:
                    st.markdown(f"<h5 style='margin-bottom: 8px;'>{cat}</h5>", unsafe_allow_html=True)
                    html_badges = ""
                    css_class = f"skill-badge-category-{(i % 5) + 1}"
                    for skill in cat_skills:
                        html_badges += f'<span class="skill-badge {css_class}">{skill}</span>'
                    st.markdown(html_badges, unsafe_allow_html=True)
                    st.markdown("<br>", unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
        st.markdown("<br>", unsafe_allow_html=True)
        st.info("Ready to see how well this candidate fits your open roles?")
        
        # Navigate using a custom message or letting user click sidebar since Streamlit doesn't support easy programmatic page change without extra hacks
        st.success("Candidate saved to session. Go to **🎯 Job Matching** in the sidebar to match with open roles.")
        
        with st.expander("View Raw Parsed Text"):
            st.text(candidate.raw_text)
