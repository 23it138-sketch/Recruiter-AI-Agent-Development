import logging
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import List, Dict, Optional
from pathlib import Path

from config import get_db_dir, PIPELINE_STAGES, DEFAULT_TIME_SLOTS
from utils import generate_id, load_json, save_json

logger = logging.getLogger(__name__)

@dataclass
class Interview:
    id: str
    candidate_name: str
    job_title: str
    date: str  # YYYY-MM-DD format
    time_slot: str
    status: str  # one of PIPELINE_STAGES
    notes: str = ""
    created_at: str = ""  # ISO format
    updated_at: str = ""  # ISO format

class InterviewScheduler:
    """Manages interview scheduling and pipeline status."""
    
    def __init__(self, db_path: Path = None):
        if db_path is None:
            db_path = get_db_dir() / "interviews.json"
        self.db_path = db_path
        self.interviews: List[Interview] = []
        self._load()
        
    def _load(self):
        """Load interviews from JSON db."""
        data = load_json(self.db_path)
        if isinstance(data, list):
            self.interviews = [Interview(**item) for item in data]
        else:
            self.interviews = []
            
    def _save(self):
        """Save interviews to JSON db."""
        data = [asdict(i) for i in self.interviews]
        save_json(self.db_path, data)
        
    def create_interview(self, candidate_name: str, job_title: str, date: str, time_slot: str, notes: str = "") -> Interview:
        """Create a new interview and persist it."""
        now = datetime.now().isoformat()
        interview = Interview(
            id=generate_id(),
            candidate_name=candidate_name,
            job_title=job_title,
            date=date,
            time_slot=time_slot,
            status="Interview",
            notes=notes,
            created_at=now,
            updated_at=now
        )
        self.interviews.append(interview)
        self._save()
        return interview
        
    def get_all_interviews(self) -> List[Interview]:
        """Return all scheduled interviews."""
        return self.interviews
        
    def get_interview(self, interview_id: str) -> Optional[Interview]:
        """Find interview by ID."""
        for i in self.interviews:
            if i.id == interview_id:
                return i
        return None
        
    def update_status(self, interview_id: str, new_status: str) -> bool:
        """Update interview pipeline status."""
        if new_status not in PIPELINE_STAGES:
            logger.error(f"Invalid status: {new_status}")
            return False
            
        interview = self.get_interview(interview_id)
        if interview:
            interview.status = new_status
            interview.updated_at = datetime.now().isoformat()
            self._save()
            return True
        return False
        
    def update_notes(self, interview_id: str, notes: str) -> bool:
        """Update interview notes."""
        interview = self.get_interview(interview_id)
        if interview:
            interview.notes = notes
            interview.updated_at = datetime.now().isoformat()
            self._save()
            return True
        return False
        
    def delete_interview(self, interview_id: str) -> bool:
        """Delete an interview."""
        initial_len = len(self.interviews)
        self.interviews = [i for i in self.interviews if i.id != interview_id]
        if len(self.interviews) < initial_len:
            self._save()
            return True
        return False
        
    def suggest_slots(self, date: str) -> List[str]:
        """Suggest available time slots for a given date."""
        booked_slots = [i.time_slot for i in self.interviews if i.date == date]
        available = [slot for slot in DEFAULT_TIME_SLOTS if slot not in booked_slots]
        return available
        
    def get_pipeline_stats(self) -> Dict[str, int]:
        """Get count of interviews by status."""
        stats = {stage: 0 for stage in PIPELINE_STAGES}
        for i in self.interviews:
            if i.status in stats:
                stats[i.status] += 1
        return stats
        
    def get_interviews_by_status(self, status: str) -> List[Interview]:
        """Get interviews filtered by status."""
        return [i for i in self.interviews if i.status == status]
