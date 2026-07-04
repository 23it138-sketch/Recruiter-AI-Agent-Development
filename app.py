import streamlit as st
import os
import json
from utils.helpers import is_valid_resume, extract_email, extract_phone, extract_entities_spacy
from utils.parser import extract_metadata, extract_text
from database.db_manager import (
    insert_candidate, 
    get_all_candidates, 
    delete_candidate,
    insert_job,
    get_all_jobs,
    insert_match,
    get_matches_for_job
)
from agents.recruiter_agent import analyze_candidate_fit
from utils.embeddings_matcher import calculate_similarity_scores

def main():
    # 1. Page Configuration (Rich premium aesthetics)
    st.set_page_config(
        page_title="AI Recruiter Agent Cockpit",
        page_icon="💼",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # 2. Sidebar Navigation and Controls
    st.sidebar.image("https://img.icons8.com/clouds/200/briefcase.png", width=100)
    st.sidebar.title("Recruitment Cockpit")
    st.sidebar.write("Manage your candidates and match them semantically using AI.")

    # Sidebar: Job Profiles Manager
    st.sidebar.write("---")
    st.sidebar.subheader("💼 Active Job Profiles")
    
    # Form to create new jobs
    with st.sidebar.expander("➕ Add New Job Description"):
        with st.form("sidebar_job_form", clear_on_submit=True):
            job_title = st.text_input("Job Title")
            job_reqs = st.text_area("Requirements / Description")
            submit_job = st.form_submit_button("Save Profile")
            if submit_job:
                if job_title and job_reqs:
                    job_id = insert_job(title=job_title, description=job_reqs)
                    st.sidebar.success(f"Saved: {job_title} (ID: {job_id})")
                else:
                    st.sidebar.error("Title and Description are required.")
    
    # Selector to pick active job
    all_jobs = get_all_jobs()
    selected_job = None
    if all_jobs:
        job_choices = {f"{job['title']} (ID: {job['id']})": job for job in all_jobs}
        choice = st.sidebar.selectbox("Select target Job Description:", list(job_choices.keys()))
        selected_job = job_choices[choice]
    else:
        st.sidebar.warning("Please create a job profile to start matching!")

    # 3. Main Dashboard Panel
    st.title("💼 AI Recruiter Agent")
    st.write(
        "Welcome to the AI Recruitment portal. This system leverages semantic vector "
        "embeddings to rank candidate resumes and parses detailed candidate reports using Google Gemini."
    )

    if selected_job:
        # Display selected job profile in a callout card
        st.info(f"🎯 **Targeting Role: {selected_job['title']}**\n\n{selected_job['description']}")
    else:
        st.warning("⚠️ No active job profile selected. Please create or select a job profile in the sidebar.")

    # Create Tab Layout for clean navigation
    tab_candidates, tab_matching = st.tabs(["👤 Candidate Profiles", "📊 AI Matching & Rankings"])

    # --- TAB 1: CANDIDATE PROFILES ---
    with tab_candidates:
        col_up, col_list = st.columns([1, 2])

        # Sub-panel: Upload resume PDF
        with col_up:
            st.subheader("📤 Upload Candidate Resume")
            uploaded_file = st.file_uploader("Drop PDF or DOCX file here...", type=["pdf", "docx"])

            if uploaded_file is not None:
                # Rule 1: File Size Check (2MB)
                max_bytes = 2 * 1024 * 1024
                if uploaded_file.size > max_bytes:
                    st.error("File exceeds 2MB limit. Please upload a smaller document.")
                else:
                    # Save file buffer to local disk
                    temp_path = os.path.join("uploads", uploaded_file.name)
                    with open(temp_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                    
                    st.info("Reading document structure...")
                    raw_text = extract_text(temp_path)

                    if raw_text:
                        # Extract metrics
                        email = extract_email(raw_text)
                        phone = extract_phone(raw_text)
                        name = os.path.splitext(uploaded_file.name)[0].replace("_", " ").replace("-", " ").title()

                        # Rule 2: Check for existing profile warnings
                        existing_cands = get_all_candidates()
                        if any(cand["email"] == email for cand in existing_cands):
                            st.warning("Candidate with this email already exists. Profile will be updated.")

                        # Write to database
                        new_id = insert_candidate(
                            name=name,
                            email=email,
                            phone=phone,
                            resume_text=raw_text,
                            file_path=temp_path
                        )
                        st.success(f"Profile created for **{name}** (ID: {new_id})!")
                        
                        # Local NLP entity parsing check (spaCy)
                        spacy_entities = extract_entities_spacy(raw_text)
                        st.write("#### 🏷️ Local NLP Entities Tagged (spaCy):")
                        st.write(f"🏢 **Organizations:** {', '.join(spacy_entities['organizations']) if spacy_entities['organizations'] else 'None found'}")
                        st.write(f"📍 **Locations/GPE:** {', '.join(spacy_entities['locations']) if spacy_entities['locations'] else 'None found'}")
                    else:
                        st.error("Failed to parse resume text. Verify it is a valid PDF or DOCX document.")

        # Sub-panel: Candidate Database Table
        with col_list:
            st.subheader("📋 Registered Candidate Directory")
            candidates = get_all_candidates()
            
            if candidates:
                # Add Name Filter Search Bar
                search_query = st.text_input("🔍 Search Candidates by Name:", "")
                
                cand_dicts = [dict(cand) for cand in candidates]
                # Filter out raw text columns to keep the table compact
                display_table = []
                for idx, cand in enumerate(cand_dicts):
                    # Filter candidates based on name query (case-insensitive)
                    if search_query.lower() in cand["name"].lower():
                        display_table.append({
                            "ID": cand["id"],
                            "Name": cand["name"],
                            "Email": cand["email"],
                            "Phone": cand["phone"],
                            "Uploaded At": cand["created_at"]
                        })
                
                if display_table:
                    st.table(display_table)
                else:
                    st.info(f"No candidates found matching: '{search_query}'")

                # Control to delete profiles
                with st.expander("🗑️ Delete Candidate Profiles"):
                    delete_id = st.number_input("Enter Candidate ID to delete", min_value=1, step=1)
                    if st.button("Delete Candidate"):
                        if delete_candidate(delete_id):
                            st.success(f"Successfully deleted candidate ID {delete_id}!")
                            st.rerun()
                        else:
                            st.error(f"Candidate ID {delete_id} not found.")
            else:
                st.info("No candidates registered in database. Upload resumes to get started.")

    # --- TAB 2: AI MATCHING & RANKINGS ---
    with tab_matching:
        if not selected_job:
            st.warning("Select or create a Job Description profile to run comparison pipelines.")
        else:
            st.subheader("📊 Match and Rank Candidates")
            st.write("Compare all registered candidate resumes with the active job specifications.")

            # Dynamic slider for threshold filtering
            min_score = st.slider("Minimum Semantic Match Threshold (%)", min_value=0, max_value=100, value=30, step=5)

            if st.button("🚀 Calculate Match Rankings"):
                all_cands = get_all_candidates()
                if not all_cands:
                    st.warning("Please upload candidate profiles in the first tab to search against.")
                else:
                    cand_list = [dict(row) for row in all_cands]
                    
                    st.info("Generating embeddings and running FAISS index searches...")
                    ranked_matches = calculate_similarity_scores(
                        job_description=selected_job["description"],
                        candidates=cand_list,
                        min_threshold=float(min_score)
                    )

                    if ranked_matches:
                        # Display ranking table
                        name_map = {c["id"]: c["name"] for c in cand_list}
                        email_map = {c["id"]: c["email"] for c in cand_list}
                        
                        rankings_results = []
                        for rank, match in enumerate(ranked_matches):
                            c_id = match["candidate_id"]
                            rankings_results.append({
                                "Rank": rank + 1,
                                "ID": c_id,
                                "Name": name_map.get(c_id, "Unknown"),
                                "Email": email_map.get(c_id, "Unknown"),
                                "Semantic Fit": f"{match['semantic_score']}%"
                            })
                        
                        st.write("### 🥇 Ranked Search Results")
                        st.table(rankings_results)
                    else:
                        st.info(f"No candidates matched above your {min_score}% threshold.")

            # AI Evaluation Detailed Section
            st.write("---")
            st.subheader("🤖 Detailed AI Candidate Assessment")
            st.write("Select a candidate to run Google Gemini deep evaluation and generate custom interview questions.")

            all_cands_for_eval = get_all_candidates()
            if all_cands_for_eval:
                cand_options = {f"{c['name']} (ID: {c['id']})": c for c in all_cands_for_eval}
                selected_cand_name = st.selectbox("Select Candidate for Deep AI Review:", list(cand_options.keys()))
                target_cand = cand_options[selected_cand_name]

                if st.button("Generate AI Assessment Report"):
                    st.info("Calling Google Gemini to evaluate applicant fit...")
                    
                    ai_report = analyze_candidate_fit(
                        resume_text=target_cand["resume_text"],
                        job_description=selected_job["description"]
                    )

                    if ai_report["match_score"] == 0.0 and "Error" in ai_report["ai_evaluation"]:
                        st.error(ai_report["ai_evaluation"])
                    else:
                        # Log the evaluation to database
                        insert_match(
                            candidate_id=target_cand["id"],
                            job_id=selected_job["id"],
                            match_score=ai_report["match_score"],
                            ai_evaluation=ai_report["ai_evaluation"],
                            generated_questions=ai_report["generated_questions"]
                        )

                        # Render Results Beautifully
                        st.success("Deep Assessment Report Generated Successfully!")
                        
                        m_col1, m_col2 = st.columns(2)
                        m_col1.metric(label="AI Fit Rating", value=f"{ai_report['match_score']}%")
                        m_col2.metric(label="Seniority Rating", value=ai_report.get("seniority_level", "N/A"))

                        st.write("#### 📝 Evaluation Summary:")
                        st.info(ai_report["ai_evaluation"])

                        st.write("#### ❓ Customized Interview Questions:")
                        for question in ai_report["generated_questions"]:
                            st.write(f"- {question}")
            else:
                st.info("No candidates registered in database to evaluate.")

if __name__ == "__main__":
    main()
