import streamlit as st
import os
from utils.helpers import is_valid_resume, extract_email, extract_phone
from utils.parser import extract_metadata, extract_text_from_pdf
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
    """
    Main function to run the Streamlit dashboard application.
    This serves as the entry point for the AI Recruiter Agent.
    """
    # Page configuration (title, icon)
    st.set_page_config(
        page_title="AI Recruiter Agent Dashboard",
        page_icon="💼",
        layout="centered"
    )

    # Title of the page
    st.title("💼 AI Recruiter Agent")

    # Introduction text
    st.subheader("Welcome to your AI Recruitment Assistant!")
    st.write(
        "This application will help you extract candidate info, compare resumes "
        "with job descriptions, and rank candidates using LangChain and Gemini."
    )

    # Section: Job Descriptions Manager
    st.write("---")
    st.subheader("💼 Job Description Profiles Manager")
    
    with st.expander("➕ Create New Job Description Profile"):
        with st.form("create_job_form", clear_on_submit=True):
            job_title_input = st.text_input("Job Title (e.g. Senior Python Developer)")
            job_desc_input = st.text_area("Job Requirements & Responsibilities")
            job_skills_input = st.text_input("Key Skills (comma separated, e.g. Python, SQLite, FAISS)")
            submit_job = st.form_submit_button("Save Job Profile")
            
            if submit_job:
                if job_title_input and job_desc_input:
                    new_job_id = insert_job(
                        title=job_title_input,
                        description=job_desc_input,
                        skills_required=job_skills_input
                    )
                    st.success(f"Successfully saved job profile: **{job_title_input}** (ID: {new_job_id})!")
                else:
                    st.error("Job Title and Job Description details are required.")

    # Dropdown selector to choose active job
    st.write("#### 🎯 Select Active Job Description:")
    all_jobs = get_all_jobs()
    
    selected_job = None
    if all_jobs:
        # Create choice strings: "Job Title (ID: X)"
        job_choices = {f"{job['title']} (ID: {job['id']})": job for job in all_jobs}
        choice = st.selectbox("Choose a job description to match candidates against:", list(job_choices.keys()))
        selected_job = job_choices[choice]
        
        st.info(f"**Selected Job Requirements:**\n\n{selected_job['description']}")
    else:
        st.warning("No job descriptions found in the database. Please create one above first!")

    # Section: Upload Resume
    st.write("---")
    st.subheader("📤 Upload Candidate Resume")
    uploaded_file = st.file_uploader("Choose a PDF resume file...", type=["pdf"])
    
    if uploaded_file is not None:
        # Rule 1: File Size Limit (2MB)
        max_bytes = 2 * 1024 * 1024  # 2 Megabytes
        if uploaded_file.size > max_bytes:
            st.error("File size exceeds the 2MB limit. Please upload a smaller file.")
        else:
            file_name = uploaded_file.name
            temp_path = os.path.join("uploads", file_name)
            
            # 1. Save uploaded file to local directory
            with open(temp_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
                
            st.info("Extracting resume text...")
            
            # 2. Parse text from the uploaded PDF
            raw_extracted_text = extract_text_from_pdf(temp_path)
            
            if raw_extracted_text:
                # 3. Extract candidate metadata using regex
                cand_email = extract_email(raw_extracted_text)
                cand_phone = extract_phone(raw_extracted_text)
                cand_name = os.path.splitext(file_name)[0].replace("_", " ").replace("-", " ").title()
                
                # Rule 2: Duplicate Candidate Warning
                existing_candidates = get_all_candidates()
                is_duplicate = any(cand["email"] == cand_email for cand in existing_candidates)
                if is_duplicate:
                    st.warning("Candidate with this email already exists in the database. Saving will overwrite their profile.")
                
                # 4. Save parsed candidate in SQLite database
                new_id = insert_candidate(
                    name=cand_name,
                    email=cand_email,
                    phone=cand_phone,
                    resume_text=raw_extracted_text,
                    file_path=temp_path
                )
                
                st.success(f"Candidate **{cand_name}** successfully parsed and saved! Database ID: `{new_id}`")
                
                # Show preview of extracted info
                st.write("#### 🔍 Extracted Details Preview:")
                col_pre1, col_pre2 = st.columns(2)
                col_pre1.write(f"**Name:** {cand_name}")
                col_pre1.write(f"**Email:** {cand_email}")
                col_pre2.write(f"**Phone:** {cand_phone}")
                
                with st.expander("Show Extracted Raw Text"):
                    st.text(raw_extracted_text[:1000] + "\n...[truncated]..." if len(raw_extracted_text) > 1000 else raw_extracted_text)
            else:
                st.error("Failed to extract any text from this PDF file.")

    # Status check
    st.success("Lesson 1: Project environment is successfully running! 🎉")

    # Displaying the helper function demonstration from the Exercise
    st.write("### 🛠️ File Validation Helper Check:")
    
    test_file_1 = "candidate_resume.pdf"
    test_file_2 = "hacked_document.exe"
    
    is_valid_1 = is_valid_resume(test_file_1)
    is_valid_2 = is_valid_resume(test_file_2)
    
    st.info(f"File: **{test_file_1}** -> Valid Resume? **{is_valid_1}** (Expected: True)")
    st.warning(f"File: **{test_file_2}** -> Valid Resume? **{is_valid_2}** (Expected: False)")

    # Displaying the parser metadata demonstration from the Lesson 2 Exercise
    st.write("### 📊 Parser Metadata Extraction Check:")
    
    dummy_resume = (
        "John Doe\n"
        "Email: john.doe@email.com | Phone: 123-456-7890\n"
        "SUMMARY\n"
        "Experienced software developer specializing in Python, AI, and cloud systems. "
        "Over 5 years of experience designing scalable backend APIs and machine learning models. "
        "Proficient in LangChain, Streamlit, PostgreSQL, and AWS. "
        "Looking to contribute to cutting-edge AI recruitment automation tools."
    )
    
    metadata = extract_metadata(dummy_resume)
    
    # Render metrics in three side-by-side columns
    col1, col2, col3 = st.columns(3)
    col1.metric(label="Word Count", value=metadata["word_count"])
    col2.metric(label="Character Count", value=metadata["char_count"])
    col3.metric(label="Est. Pages", value=metadata["estimated_pages"])

    # Displaying the database SQLite demonstration from the Lesson 3 Exercise
    st.write("### 🗄️ Database SQLite Operations Check:")
    
    # 1. Insert a candidate (Jane Smith)
    jane_email = "jane.smith@example.com"
    jane_id = insert_candidate(
        name="Jane Smith",
        email=jane_email,
        phone="555-0199",
        resume_text="Jane Smith resume text. Skills: Python, SQL, Streamlit."
    )
    
    st.write(f"Candidate **Jane Smith** is registered in database. ID: `{jane_id}`.")
    
    # 2. Add button to delete Jane Smith
    if st.button("Delete Jane Smith"):
        deleted = delete_candidate(jane_id)
        if deleted:
            st.success("Successfully deleted Jane Smith from the database! Refresh to update.")
        else:
            st.error("Failed to delete candidate or candidate already deleted.")

    # 3. Retrieve and list all candidates in the database
    st.write("#### 📋 Current Registered Candidates Table:")
    candidates_list = get_all_candidates()
    if candidates_list:
        # Convert SQLite row objects into dicts so Streamlit can format it in a clean table
        table_data = [dict(row) for row in candidates_list]
        st.table(table_data)
    else:
        st.info("No candidates registered in database.")

    # Displaying the AI recruiter analysis check from the Lesson 4 Exercise
    st.write("### 🤖 AI Recruiter Agent Analysis Check:")
    
    if selected_job:
        active_jd = selected_job["description"]
        active_job_id = selected_job["id"]
        st.write(f"Evaluating test candidate **Jane Smith** against: **{selected_job['title']}**")
        
        # Run the AI evaluation (will catch if API Key is not set)
        ai_result = analyze_candidate_fit(
            resume_text=dummy_resume,
            job_description=active_jd
        )
        
        st.write("**AI Evaluation Results:**")
        if ai_result["match_score"] == 0.0 and "Error" in ai_result["ai_evaluation"]:
            st.error(ai_result["ai_evaluation"])
        else:
            col_ai1, col_ai2 = st.columns(2)
            col_ai1.metric(label="Match Score", value=f"{ai_result['match_score']}%")
            col_ai2.metric(label="Seniority Level", value=ai_result.get("seniority_level", "N/A"))
            
            st.write("**Detailed Assessment:**")
            st.info(ai_result["ai_evaluation"])
            
            st.write("**Suggested Interview Questions:**")
            for q in ai_result["generated_questions"]:
                st.write(f"- {q}")
            
            # Save the AI evaluation result to our SQL matches table
            match_id = insert_match(
                candidate_id=jane_id,
                job_id=active_job_id,
                match_score=ai_result["match_score"],
                ai_evaluation=ai_result["ai_evaluation"],
                generated_questions=ai_result["generated_questions"]
            )
            st.write(f"Persistent Match logged in SQLite matches table. Match ID: `{match_id}`.")
    else:
        st.info("Please create and select a job description above to test AI matching.")

    # Displaying the semantic search matching from the Lesson 6 Exercise
    st.write("---")
    st.write("### 🔍 Candidate Semantic Search Matching (FAISS):")
    
    search_jd = st.text_area(
        label="Enter Job Requirements for Search",
        value=selected_job["description"] if selected_job else "Looking for a Python developer who knows SQL, database modeling, and building Streamlit dashboards."
    )
    
    min_threshold = st.slider(
        label="Minimum Match Threshold (%)",
        min_value=0.0,
        max_value=100.0,
        value=30.0,
        step=5.0
    )
    
    if st.button("Run Semantic Matcher"):
        # Fetch candidates from the database
        db_candidates = get_all_candidates()
        if db_candidates:
            # Convert SQLite rows to dictionary list
            cand_dicts = [dict(row) for row in db_candidates]
            
            # Run embedding similarity scoring
            scores_list = calculate_similarity_scores(
                job_description=search_jd,
                candidates=cand_dicts,
                min_threshold=min_threshold
            )
            
            if scores_list:
                # Merge candidate names into scores representation
                name_lookup = {cand["id"]: cand["name"] for cand in cand_dicts}
                
                results_table = []
                for idx, match_item in enumerate(scores_list):
                    c_id = match_item["candidate_id"]
                    results_table.append({
                        "Rank": idx + 1,
                        "Candidate ID": c_id,
                        "Candidate Name": name_lookup.get(c_id, "Unknown"),
                        "Semantic Match Score": f"{match_item['semantic_score']}%"
                    })
                
                st.write("**Matching Candidates Ranked:**")
                st.table(results_table)
            else:
                st.info(f"No candidates matched above the {min_threshold}% threshold.")
        else:
            st.info("No candidates registered in database to search against.")

if __name__ == "__main__":
    main()
