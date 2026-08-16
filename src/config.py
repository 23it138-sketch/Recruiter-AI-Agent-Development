import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Paths
PROJECT_ROOT = Path(__file__).parent.parent
SRC_DIR = Path(__file__).parent
DATA_DIR = PROJECT_ROOT / "data"
UPLOAD_DIR = PROJECT_ROOT / "uploaded_resumes"
DB_DIR = PROJECT_ROOT / "db"

# Gemini
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")

# App
APP_NAME = "Recruiter AI Agent"
APP_VERSION = "1.0.0"
MAX_UPLOAD_SIZE_MB = 10
SUPPORTED_FILE_TYPES = ["pdf", "txt"]

# Interview time slots
DEFAULT_TIME_SLOTS = [
    "09:00 AM - 09:45 AM",
    "10:00 AM - 10:45 AM",
    "11:00 AM - 11:45 AM",
    "01:00 PM - 01:45 PM",
    "02:00 PM - 02:45 PM",
    "03:00 PM - 03:45 PM",
    "04:00 PM - 04:45 PM",
]

# Pipeline stages
PIPELINE_STAGES = ["Applied", "Screening", "Interview", "Selected", "Rejected"]

def is_gemini_available() -> bool:
    return bool(GEMINI_API_KEY and GEMINI_API_KEY.strip())

def get_data_dir() -> Path:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    return DATA_DIR

def get_upload_dir() -> Path:
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    return UPLOAD_DIR

def get_db_dir() -> Path:
    DB_DIR.mkdir(parents=True, exist_ok=True)
    return DB_DIR
