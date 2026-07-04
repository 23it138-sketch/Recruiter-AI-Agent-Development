import streamlit as st

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

if __name__ == "__main__":
    main()
