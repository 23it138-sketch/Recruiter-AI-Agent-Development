import logging
import json
import re
from dataclasses import dataclass, field
from typing import Any
from pypdf import PdfReader
from gemini_client import get_gemini_client
from utils import clean_text

logger = logging.getLogger(__name__)

@dataclass
class ResumeData:
    name: str = ""
    email: str = ""
    phone: str = ""
    education: list[str] = field(default_factory=list)
    experience: list[str] = field(default_factory=list)
    skills: list[str] = field(default_factory=list)
    certifications: list[str] = field(default_factory=list)
    projects: list[str] = field(default_factory=list)
    summary: str = ""
    raw_text: str = ""

class ResumeParser:
    """Parser to extract structured data from resumes."""
    
    def parse_pdf(self, file: Any) -> str:
        """Extract text from a PDF file-like object."""
        try:
            reader = PdfReader(file)
            text = ""
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
            return text
        except Exception as e:
            logger.error(f"Failed to parse PDF: {e}")
            return f"Error parsing PDF: {str(e)}"
    
    def parse_txt(self, file_or_bytes: Any) -> str:
        """Extract text from a text file or bytes."""
        try:
            if isinstance(file_or_bytes, bytes):
                return file_or_bytes.decode('utf-8', errors='ignore')
            elif hasattr(file_or_bytes, 'read'):
                content = file_or_bytes.read()
                if isinstance(content, bytes):
                    return content.decode('utf-8', errors='ignore')
                return content
            return str(file_or_bytes)
        except Exception as e:
            logger.error(f"Failed to parse TXT: {e}")
            return f"Error parsing text: {str(e)}"
            
    def extract_info(self, text: str) -> ResumeData:
        """Extract structured information from resume text using Gemini or regex fallback."""
        client = get_gemini_client()
        
        if client.is_available:
            cleaned = clean_text(text)
            prompt = f"""
Extract the following information from the resume text provided below. 
Return the output ONLY as a valid JSON object with the following keys exactly:
"name" (string), "email" (string), "phone" (string), "education" (array of strings),
"experience" (array of strings), "skills" (array of strings),
"certifications" (array of strings), "projects" (array of strings), "summary" (string).

Resume Text:
{cleaned}
"""
            response = client.generate(prompt)
            if response:
                try:
                    # Clean markdown code fences if present
                    json_str = response.strip()
                    if json_str.startswith("```json"):
                        json_str = json_str[7:]
                    elif json_str.startswith("```"):
                        json_str = json_str[3:]
                    if json_str.endswith("```"):
                        json_str = json_str[:-3]
                        
                    data = json.loads(json_str.strip())
                    return ResumeData(
                        name=data.get("name", ""),
                        email=data.get("email", ""),
                        phone=data.get("phone", ""),
                        education=data.get("education", []),
                        experience=data.get("experience", []),
                        skills=data.get("skills", []),
                        certifications=data.get("certifications", []),
                        projects=data.get("projects", []),
                        summary=data.get("summary", ""),
                        raw_text=text
                    )
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse Gemini JSON output: {e}\nResponse: {response}")
        
        # Fallback to regex extraction — use original text with newlines preserved
        logger.info("Falling back to regex extraction for resume.")
        data = self._regex_extract(text)
        data.raw_text = text
        return data

    def _regex_extract(self, text: str) -> ResumeData:
        """Fallback extraction using regular expressions."""
        email_match = re.search(r'[\w.+-]+@[\w-]+\.[\w.-]+', text)
        email = email_match.group(0) if email_match else ""
        
        phone_match = re.search(r'\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}', text)
        phone = phone_match.group(0) if phone_match else ""
        
        # Simple heuristic for name: first non-empty short line
        name = ""
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        if lines:
            for line in lines[:5]:
                if len(line.split()) <= 4 and not re.search(r'\d', line):
                    name = line
                    break
        
        skills = []
        common_skills = ['python', 'java', 'javascript', 'c++', 'sql', 'react', 'aws', 'docker', 'machine learning', 'agile']
        text_lower = text.lower()
        for skill in common_skills:
            if re.search(r'\b' + re.escape(skill) + r'\b', text_lower):
                skills.append(skill)
                
        education = []
        if re.search(r'\b(bachelor|master|phd|b\.s|m\.s|university|college)\b', text_lower):
            lines_lower = [l.lower() for l in lines]
            for i, l in enumerate(lines_lower):
                if any(k in l for k in ['bachelor', 'master', 'university', 'degree']):
                    education.append(lines[i])
                    
        return ResumeData(name=name, email=email, phone=phone, skills=skills, education=education)
