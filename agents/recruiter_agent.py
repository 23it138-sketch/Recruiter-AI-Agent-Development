import os
import json
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.pydantic_v1 import BaseModel, Field

# Load API keys from .env file
load_dotenv()

# Define the structure we want the AI to return using Pydantic
class CandidateEvaluation(BaseModel):
    match_score: float = Field(description="A score from 0.0 to 100.0 indicating how well the candidate matches the job description.")
    ai_evaluation: str = Field(description="A brief, professional 3-4 sentence paragraph summarizing the candidate's fit, strengths, and gaps.")
    seniority_level: str = Field(description="The candidate's seniority level based on experience. Must be one of: 'Junior', 'Mid', or 'Senior'.")
    generated_questions: list = Field(description="A list of 3-5 technical and behavioral interview questions tailored to the candidate's profile for this job.")


def analyze_candidate_fit(resume_text: str, job_description: str) -> dict:
    """
    Leverages LangChain and Google Gemini to evaluate how well a candidate's
    parsed resume matches a given job description.

    Args:
        resume_text (str): The clean extracted text of the candidate's resume.
        job_description (str): The job requirements.

    Returns:
        dict: Evaluated metrics (match_score, ai_evaluation, generated_questions).
    """
    # 1. Ensure the Gemini API key is configured
    api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
    if not api_key:
        return {
            "match_score": 0.0,
            "ai_evaluation": "Error: Google/Gemini API Key is not configured. Please add GEMINI_API_KEY to your .env file.",
            "generated_questions": []
        }

    try:
        # 2. Initialize the Gemini LLM via LangChain
        # We use gemini-1.5-flash as it is fast, cheap, and excellent for structured extraction
        llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            google_api_key=api_key,
            temperature=0.2  # Low temperature makes the output more deterministic/factual
        )

        # 3. Setup the JSON Output Parser based on our Pydantic schema
        parser = JsonOutputParser(pydantic_object=CandidateEvaluation)

        # 4. Create the prompt template instructing the AI how to behave
        prompt_template = """
        You are an expert technical recruiter and talent advisor. 
        Your task is to evaluate the candidate's resume text against the provided job description.
        
        {format_instructions}
        
        Job Description:
        {job_description}
        
        Candidate Resume:
        {resume_text}
        
        Conduct a thorough analysis, compute an objective match score (0 to 100), and write a professional evaluation.
        """

        prompt = PromptTemplate(
            template=prompt_template,
            input_variables=["job_description", "resume_text"],
            partial_variables={"format_instructions": parser.get_format_instructions()}
        )

        # 5. Chain the prompt, model, and parser together using LangChain Expression Language (LCEL)
        chain = prompt | llm | parser

        # 6. Execute the chain
        result = chain.invoke({
            "job_description": job_description,
            "resume_text": resume_text
        })

        return result

    except Exception as e:
        print(f"Error during AI candidate evaluation: {e}")
        return {
            "match_score": 0.0,
            "ai_evaluation": f"An error occurred during evaluation: {str(e)}",
            "generated_questions": []
        }
