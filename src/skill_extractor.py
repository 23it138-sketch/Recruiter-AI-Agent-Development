import logging
import re
from typing import Dict, List, Set
from gemini_client import get_gemini_client

logger = logging.getLogger(__name__)

SKILL_DATABASE = {
    "Programming Languages": ["python", "java", "javascript", "typescript", "c++", "c#", "go", "rust", "ruby", "php", "swift", "kotlin", "scala", "r", "matlab", "sql", "html", "css"],
    "Frameworks & Libraries": ["react", "angular", "vue", "django", "flask", "fastapi", "spring", "express", "next.js", "node.js", ".net", "tensorflow", "pytorch", "pandas", "numpy", "scikit-learn", "streamlit", "bootstrap", "tailwind"],
    "Databases": ["mysql", "postgresql", "mongodb", "redis", "sqlite", "oracle", "cassandra", "dynamodb", "elasticsearch", "firebase"],
    "Cloud & DevOps": ["aws", "azure", "gcp", "docker", "kubernetes", "terraform", "jenkins", "github actions", "ci/cd", "linux", "nginx", "apache"],
    "Data & AI": ["machine learning", "deep learning", "nlp", "computer vision", "data analysis", "data engineering", "etl", "tableau", "power bi", "spark", "hadoop", "airflow"],
    "Tools & Practices": ["git", "jira", "confluence", "agile", "scrum", "rest api", "graphql", "microservices", "tdd", "unit testing"],
    "Soft Skills": ["leadership", "communication", "teamwork", "problem solving", "project management", "mentoring", "critical thinking", "time management"]
}

class SkillExtractor:
    """Extract and categorize skills from text."""
    
    def extract(self, text: str) -> List[str]:
        """Extract skills from text by matching against SKILL_DATABASE and using Gemini if available."""
        if not text:
            return []
            
        found_skills = set()
        text_lower = text.lower()
        
        # Regex matching
        for category, skills in SKILL_DATABASE.items():
            for skill in skills:
                # Use word boundaries for precise matching
                if re.search(r'\b' + re.escape(skill) + r'\b', text_lower):
                    found_skills.add(skill)
                    
        # Optional: Use Gemini for smarter extraction
        client = get_gemini_client()
        if client.is_available:
            prompt = f"""
Given the following resume text, extract a comma-separated list of technical and soft skills.
Only return the comma-separated list, nothing else. Do not use quotes.
Text:
{text[:2000]}
"""
            response = client.generate(prompt)
            if response:
                ai_skills = [s.strip().lower() for s in response.split(',')]
                found_skills.update(ai_skills)
                
        return self.normalize(list(found_skills))
        
    def normalize(self, skills: List[str]) -> List[str]:
        """Lowercase, deduplicate, and sort skills."""
        if not skills:
            return []
        unique_skills = set(s.lower().strip() for s in skills if s.strip())
        return sorted(list(unique_skills))
        
    def categorize(self, skills: List[str]) -> Dict[str, List[str]]:
        """Group extracted skills by category using SKILL_DATABASE."""
        categorized = {cat: [] for cat in SKILL_DATABASE.keys()}
        categorized["Other"] = []
        
        normalized_skills = self.normalize(skills)
        all_known = self.get_all_known_skills()
        
        for skill in normalized_skills:
            found_category = False
            for cat, cat_skills in SKILL_DATABASE.items():
                if skill in cat_skills:
                    categorized[cat].append(skill)
                    found_category = True
                    break
            
            if not found_category:
                categorized["Other"].append(skill)
                
        # Remove empty categories
        return {k: v for k, v in categorized.items() if v}
        
    def get_all_known_skills(self) -> Set[str]:
        """Flatten SKILL_DATABASE into a set of known skills."""
        known = set()
        for skills in SKILL_DATABASE.values():
            known.update(skills)
        return known
