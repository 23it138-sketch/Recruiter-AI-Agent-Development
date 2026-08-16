"""Smoke and unit tests for Recruiter AI Agent."""
import sys
import os
import json
import tempfile
from pathlib import Path

# Add src/ to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Ensure no API key is set during tests (test graceful degradation)
os.environ.pop("GEMINI_API_KEY", None)

import pytest


# ─── Config Tests ───────────────────────────────────────────────────

class TestConfig:
    def test_imports(self):
        import config
        assert config.APP_NAME == "Recruiter AI Agent"
        assert config.APP_VERSION == "1.0.0"
    
    def test_gemini_unavailable_without_key(self):
        import config
        assert config.is_gemini_available() is False
    
    def test_pipeline_stages(self):
        import config
        expected = ["Applied", "Screening", "Interview", "Selected", "Rejected"]
        assert config.PIPELINE_STAGES == expected
    
    def test_paths_exist(self):
        import config
        assert config.PROJECT_ROOT.exists()
        assert config.SRC_DIR.exists()
        assert config.DATA_DIR.exists()
    
    def test_get_dirs_create_on_demand(self):
        import config
        # These should create dirs if they don't exist
        data = config.get_data_dir()
        assert data.exists()


# ─── Utils Tests ────────────────────────────────────────────────────

class TestUtils:
    def test_generate_id(self):
        from utils import generate_id
        uid = generate_id()
        assert isinstance(uid, str)
        assert len(uid) == 8
    
    def test_generate_id_unique(self):
        from utils import generate_id
        ids = {generate_id() for _ in range(100)}
        assert len(ids) == 100  # All unique
    
    def test_clean_text(self):
        from utils import clean_text
        assert clean_text("  hello   world  ") == "hello world"
        assert clean_text("") == ""
        assert clean_text(None) == ""
    
    def test_load_json_missing_file(self):
        from utils import load_json
        result = load_json("/nonexistent/path/file.json")
        assert result == {}
    
    def test_save_and_load_json(self):
        from utils import save_json, load_json
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "test.json"
            data = {"key": "value", "list": [1, 2, 3]}
            save_json(path, data)
            loaded = load_json(path)
            assert loaded == data
    
    def test_save_and_load_json_list(self):
        from utils import save_json, load_json
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "test.json"
            data = [{"id": 1}, {"id": 2}]
            save_json(path, data)
            loaded = load_json(path)
            assert loaded == data
    
    def test_get_file_extension(self):
        from utils import get_file_extension
        assert get_file_extension("resume.pdf") == "pdf"
        assert get_file_extension("document.TXT") == "txt"
        assert get_file_extension("noext") == ""
        assert get_file_extension("") == ""
    
    def test_validate_file_no_file(self):
        from utils import validate_file
        valid, msg = validate_file(None, ["pdf", "txt"], 10)
        assert valid is False


# ─── Gemini Client Tests ───────────────────────────────────────────

class TestGeminiClient:
    def test_import(self):
        from gemini_client import GeminiClient, get_gemini_client
    
    def test_unavailable_without_key(self):
        from gemini_client import GeminiClient
        client = GeminiClient(api_key="", model="gemini-2.0-flash")
        assert client.is_available is False
    
    def test_generate_returns_none_when_unavailable(self):
        from gemini_client import GeminiClient
        client = GeminiClient(api_key="", model="gemini-2.0-flash")
        result = client.generate("Hello")
        assert result is None
    
    def test_chat_returns_none_when_unavailable(self):
        from gemini_client import GeminiClient
        client = GeminiClient(api_key="", model="gemini-2.0-flash")
        result = client.chat([{"role": "user", "content": "Hi"}])
        assert result is None


# ─── Resume Parser Tests ──────────────────────────────────────────

class TestResumeParser:
    def test_import(self):
        from resume_parser import ResumeParser, ResumeData
    
    def test_parse_txt_string(self):
        from resume_parser import ResumeParser
        parser = ResumeParser()
        text = parser.parse_txt(b"Hello World")
        assert text == "Hello World"
    
    def test_extract_email(self):
        from resume_parser import ResumeParser
        parser = ResumeParser()
        text = "John Doe\njohn@example.com\n(555) 123-4567"
        data = parser.extract_info(text)
        assert data.email == "john@example.com"
    
    def test_extract_phone(self):
        from resume_parser import ResumeParser
        parser = ResumeParser()
        text = "Jane Smith\njane@test.com\n(555) 987-6543"
        data = parser.extract_info(text)
        assert "555" in data.phone
    
    def test_extract_name(self):
        from resume_parser import ResumeParser
        parser = ResumeParser()
        text = "John Doe\njohn@example.com\n(555) 123-4567\nSKILLS: Python"
        data = parser.extract_info(text)
        assert data.name == "John Doe"
    
    def test_extract_skills(self):
        from resume_parser import ResumeParser
        parser = ResumeParser()
        text = "I know Python and Java and AWS and Docker"
        data = parser.extract_info(text)
        assert "python" in data.skills
        assert "java" in data.skills
    
    def test_malformed_pdf(self):
        """Test that malformed PDF doesn't crash."""
        from resume_parser import ResumeParser
        import io
        parser = ResumeParser()
        fake_pdf = io.BytesIO(b"This is not a real PDF")
        result = parser.parse_pdf(fake_pdf)
        assert isinstance(result, str)  # Should return error message, not crash
    
    def test_sample_resume_parsing(self):
        """Parse a real sample resume."""
        from resume_parser import ResumeParser
        import config
        parser = ResumeParser()
        sample_path = config.DATA_DIR / "sample_resumes" / "john_doe_software_engineer.txt"
        if sample_path.exists():
            text = sample_path.read_text()
            data = parser.extract_info(text)
            assert data.name  # Should extract a name
            assert data.email  # Should extract email
            assert len(data.skills) > 0  # Should extract some skills


# ─── Skill Extractor Tests ────────────────────────────────────────

class TestSkillExtractor:
    def test_import(self):
        from skill_extractor import SkillExtractor, SKILL_DATABASE
    
    def test_extract(self):
        from skill_extractor import SkillExtractor
        extractor = SkillExtractor()
        skills = extractor.extract("I use Python, React, and Docker")
        assert "python" in skills
        assert "react" in skills
        assert "docker" in skills
    
    def test_normalize(self):
        from skill_extractor import SkillExtractor
        extractor = SkillExtractor()
        result = extractor.normalize(["Python", "python", "PYTHON", "Java"])
        assert result == ["java", "python"]  # Deduped, sorted, lowercase
    
    def test_categorize(self):
        from skill_extractor import SkillExtractor
        extractor = SkillExtractor()
        categorized = extractor.categorize(["python", "react", "aws"])
        assert "Programming Languages" in categorized
        assert "python" in categorized["Programming Languages"]
    
    def test_empty_input(self):
        from skill_extractor import SkillExtractor
        extractor = SkillExtractor()
        assert extractor.extract("") == []
        assert extractor.normalize([]) == []
    
    def test_get_all_known_skills(self):
        from skill_extractor import SkillExtractor
        extractor = SkillExtractor()
        known = extractor.get_all_known_skills()
        assert len(known) > 50  # Should have many known skills


# ─── Job Matcher Tests ────────────────────────────────────────────

class TestJobMatcher:
    def test_import(self):
        from job_matcher import JobMatcher, MatchResult
    
    def test_match_basic(self):
        from job_matcher import JobMatcher
        from resume_parser import ResumeData
        matcher = JobMatcher()
        
        candidate = ResumeData(
            name="Test",
            skills=["python", "aws", "docker"],
            raw_text="Python developer with AWS experience"
        )
        job = {
            "title": "Backend Developer",
            "requirements": ["python", "aws", "docker", "java"],
            "description": "Backend developer needed",
            "experience_required": "3+ years",
            "education_required": "Bachelor's"
        }
        result = matcher.match(candidate, job)
        assert 0 <= result.score <= 100
        assert "python" in result.matched_skills
        assert "java" in result.missing_skills
    
    def test_match_all_jobs(self):
        from job_matcher import JobMatcher
        from resume_parser import ResumeData
        from utils import load_json
        import config
        
        matcher = JobMatcher()
        candidate = ResumeData(
            name="Test",
            skills=["python", "java", "aws"],
            raw_text="Software engineer with Python Java AWS experience"
        )
        
        jobs = load_json(config.DATA_DIR / "sample_jobs.json")
        if jobs:
            results = matcher.match_all_jobs(candidate, jobs)
            assert len(results) == len(jobs)
            # Should be sorted descending by score
            scores = [r.score for _, r in results]
            assert scores == sorted(scores, reverse=True)


# ─── Scheduler Tests ──────────────────────────────────────────────

class TestScheduler:
    def test_import(self):
        from scheduler import InterviewScheduler, Interview
    
    def test_create_and_retrieve(self):
        from scheduler import InterviewScheduler
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test_interviews.json"
            sched = InterviewScheduler(db_path=db_path)
            
            inv = sched.create_interview("John Doe", "Software Engineer", "2025-01-15", "09:00 AM - 09:45 AM", "Initial interview")
            assert inv.candidate_name == "John Doe"
            assert inv.status == "Interview"
            
            all_inv = sched.get_all_interviews()
            assert len(all_inv) == 1
    
    def test_update_status(self):
        from scheduler import InterviewScheduler
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test_interviews.json"
            sched = InterviewScheduler(db_path=db_path)
            inv = sched.create_interview("Jane", "PM", "2025-02-01", "10:00 AM - 10:45 AM")
            
            result = sched.update_status(inv.id, "Selected")
            assert result is True
            updated = sched.get_interview(inv.id)
            assert updated.status == "Selected"
    
    def test_invalid_status(self):
        from scheduler import InterviewScheduler
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test_interviews.json"
            sched = InterviewScheduler(db_path=db_path)
            inv = sched.create_interview("Test", "Role", "2025-01-01", "09:00 AM - 09:45 AM")
            
            result = sched.update_status(inv.id, "InvalidStatus")
            assert result is False
    
    def test_delete(self):
        from scheduler import InterviewScheduler
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test_interviews.json"
            sched = InterviewScheduler(db_path=db_path)
            inv = sched.create_interview("To Delete", "Role", "2025-01-01", "09:00 AM - 09:45 AM")
            
            sched.delete_interview(inv.id)
            assert sched.get_interview(inv.id) is None
    
    def test_suggest_slots(self):
        from scheduler import InterviewScheduler
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test_interviews.json"
            sched = InterviewScheduler(db_path=db_path)
            
            slots = sched.suggest_slots("2025-03-01")
            assert len(slots) == 7  # All slots available
            
            # Book one slot
            sched.create_interview("Test", "Role", "2025-03-01", slots[0])
            remaining = sched.suggest_slots("2025-03-01")
            assert len(remaining) == 6
    
    def test_pipeline_stats(self):
        from scheduler import InterviewScheduler
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test_interviews.json"
            sched = InterviewScheduler(db_path=db_path)
            
            stats = sched.get_pipeline_stats()
            assert sum(stats.values()) == 0
    
    def test_persistence(self):
        """Data should persist across instances."""
        from scheduler import InterviewScheduler
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test_interviews.json"
            
            sched1 = InterviewScheduler(db_path=db_path)
            sched1.create_interview("Persist", "Test", "2025-01-01", "09:00 AM - 09:45 AM")
            
            sched2 = InterviewScheduler(db_path=db_path)
            assert len(sched2.get_all_interviews()) == 1


# ─── Chat Agent Tests ─────────────────────────────────────────────

class TestChatAgent:
    def test_import(self):
        from chat_agent import ChatAgent
    
    def test_unavailable_without_key(self):
        from chat_agent import ChatAgent
        agent = ChatAgent()
        assert agent.is_available is False
    
    def test_chat_without_key_returns_message(self):
        from chat_agent import ChatAgent
        agent = ChatAgent()
        response = agent.chat("Hello")
        assert "GEMINI_API_KEY" in response or "unavailable" in response.lower()
    
    def test_clear_history(self):
        from chat_agent import ChatAgent
        agent = ChatAgent()
        agent.chat("Hello")
        agent.clear_history()
        assert len(agent.history) == 0


# ─── Sample Data Tests ────────────────────────────────────────────

class TestSampleData:
    def test_sample_jobs_exist(self):
        import config
        jobs_path = config.DATA_DIR / "sample_jobs.json"
        assert jobs_path.exists()
    
    def test_sample_jobs_valid(self):
        import config
        from utils import load_json
        jobs = load_json(config.DATA_DIR / "sample_jobs.json")
        assert isinstance(jobs, list)
        assert len(jobs) >= 5
        
        for job in jobs:
            assert "id" in job
            assert "title" in job
            assert "company" in job
            assert "requirements" in job
            assert isinstance(job["requirements"], list)
    
    def test_sample_resumes_exist(self):
        import config
        resumes_dir = config.DATA_DIR / "sample_resumes"
        assert resumes_dir.exists()
        txt_files = list(resumes_dir.glob("*.txt"))
        assert len(txt_files) >= 3


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
