import logging
import re
from dataclasses import dataclass, field
from typing import List, Dict, Tuple
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from resume_parser import ResumeData
from skill_extractor import SkillExtractor

logger = logging.getLogger(__name__)

@dataclass
class MatchResult:
    score: float  # 0-100 percentage
    matched_skills: List[str]
    missing_skills: List[str]
    strengths: List[str]
    weaknesses: List[str]
    recommendation: str
    skill_score: float  # 0-100
    experience_score: float  # 0-100
    education_score: float  # 0-100

class JobMatcher:
    """Matches candidate resumes against job descriptions."""
    
    def __init__(self):
        self.vectorizer = TfidfVectorizer(stop_words='english')
        self.skill_extractor = SkillExtractor()
        
    def match(self, candidate: ResumeData, job: Dict) -> MatchResult:
        """Score candidate against a job description."""
        # 1. Skill matching
        job_skills = set(job.get("requirements", []) + job.get("skills", []))
        job_skills = set(s.lower() for s in job_skills)
        if not job_skills and "description" in job:
            job_skills = set(self.skill_extractor.extract(job["description"]))
            
        candidate_skills = set(s.lower() for s in candidate.skills)
        
        matched_skills = list(job_skills.intersection(candidate_skills))
        missing_skills = list(job_skills.difference(candidate_skills))
        
        skill_score = 0.0
        if job_skills:
            skill_score = (len(matched_skills) / len(job_skills)) * 100
        else:
            skill_score = 100.0 if candidate_skills else 0.0
            
        # 2. Text similarity
        text_similarity = 0.0
        try:
            job_desc = job.get("description", "") + " " + " ".join(job.get("responsibilities", []))
            if candidate.raw_text and job_desc:
                tfidf_matrix = self.vectorizer.fit_transform([candidate.raw_text, job_desc])
                similarity_matrix = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])
                text_similarity = similarity_matrix[0][0] * 100
        except Exception as e:
            logger.warning(f"TF-IDF similarity calculation failed: {e}")
            
        # 3. Experience matching (simplified)
        exp_req = str(job.get("experience_required", "")).lower()
        req_years = 0
        match = re.search(r'(\d+)', exp_req)
        if match:
            req_years = int(match.group(1))
            
        candidate_exp_text = " ".join(candidate.experience).lower()
        candidate_years = 0
        matches = re.findall(r'(\d+)\+? years?', candidate_exp_text)
        if matches:
            candidate_years = max([int(m) for m in matches])
            
        experience_score = min(100.0, (candidate_years / max(1, req_years)) * 100) if req_years > 0 else 100.0
        
        # 4. Education matching (simplified)
        edu_req = str(job.get("education_required", "")).lower()
        candidate_edu = " ".join(candidate.education).lower()
        
        education_score = 50.0 # Default
        if not edu_req:
            education_score = 100.0
        else:
            req_degree = "bachelor" if "bachelor" in edu_req or "b.s" in edu_req else \
                         "master" if "master" in edu_req or "m.s" in edu_req else \
                         "phd" if "phd" in edu_req else ""
                         
            if req_degree and req_degree in candidate_edu:
                education_score = 100.0
            elif "phd" in candidate_edu and req_degree in ["bachelor", "master"]:
                education_score = 100.0
            elif "master" in candidate_edu and req_degree == "bachelor":
                education_score = 100.0
            elif req_degree:
                education_score = 20.0
                
        # 5. Weighted score
        total_score = (skill_score * 0.40) + (text_similarity * 0.25) + (experience_score * 0.20) + (education_score * 0.15)
        
        # 6. Generate strengths, weaknesses, recommendation
        strengths = []
        weaknesses = []
        
        if skill_score > 75:
            strengths.append(f"Strong skill alignment ({len(matched_skills)} matching skills)")
        elif skill_score < 40:
            weaknesses.append(f"Missing several key skills ({len(missing_skills)} missing)")
            
        if experience_score == 100 and req_years > 0:
            strengths.append("Meets or exceeds experience requirements")
        elif experience_score < 50 and req_years > 0:
            weaknesses.append("May lack required years of experience")
            
        if total_score > 75:
            recommendation = "Strong match. Candidate has most of the required skills and relevant background. Consider for interview."
        elif total_score > 50:
            recommendation = "Moderate match. Candidate meets some requirements but may have gaps. Consider for phone screen."
        else:
            recommendation = "Weak match. Candidate lacks significant requirements for this role."
            
        return MatchResult(
            score=round(total_score, 2),
            matched_skills=matched_skills,
            missing_skills=missing_skills,
            strengths=strengths,
            weaknesses=weaknesses,
            recommendation=recommendation,
            skill_score=round(skill_score, 2),
            experience_score=round(experience_score, 2),
            education_score=round(education_score, 2)
        )
        
    def match_all_jobs(self, candidate: ResumeData, jobs: List[Dict]) -> List[Tuple[Dict, MatchResult]]:
        """Match against all jobs, return sorted by score descending."""
        results = []
        for job in jobs:
            result = self.match(candidate, job)
            results.append((job, result))
            
        results.sort(key=lambda x: x[1].score, reverse=True)
        return results
