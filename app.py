import streamlit as st
from utils.helpers import is_valid_resume
from utils.parser import extract_metadata
from database.db_manager import insert_candidate, get_all_candidates, delete_candidate

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

if __name__ == "__main__":
    main()
