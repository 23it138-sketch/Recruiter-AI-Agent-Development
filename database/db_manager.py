import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "recruiter.db")

def get_db_connection():
    """
    Establishes and returns a connection to the SQLite database.
    Enables Row factory to access column names like a dictionary.
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """
    Creates tables in the SQLite database if they do not exist.
    Schema includes:
    1. candidates: holds candidate profile and resume text.
    2. jobs: holds job descriptions.
    3. matches: stores AI match scores and interview questions.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    # 1. Create candidates table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS candidates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE,
            phone TEXT,
            skills TEXT,
            experience_summary TEXT,
            resume_text TEXT NOT NULL,
            file_path TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # 2. Create jobs table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            skills_required TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # 3. Create matches table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS matches (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            candidate_id INTEGER NOT NULL,
            job_id INTEGER NOT NULL,
            match_score REAL,
            ai_evaluation TEXT,
            generated_questions TEXT,
            matched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (candidate_id) REFERENCES candidates (id) ON DELETE CASCADE,
            FOREIGN KEY (job_id) REFERENCES jobs (id) ON DELETE CASCADE,
            UNIQUE(candidate_id, job_id)
        )
    """)

    conn.commit()
    conn.close()
    print("Database tables initialized successfully.")


def insert_candidate(name: str, email: str, phone: str, resume_text: str, file_path: str = None) -> int:
    """
    Inserts a new candidate into the candidates table.
    If the candidate's email already exists, it updates their profile.

    Args:
        name (str): Full name of the candidate.
        email (str): Candidate email address.
        phone (str): Candidate contact number.
        resume_text (str): Extracted clean text of the resume.
        file_path (str, optional): System path where raw file is stored.

    Returns:
        int: The ID of the inserted or updated candidate.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Check if email already exists
        cursor.execute("SELECT id FROM candidates WHERE email = ?", (email,))
        row = cursor.fetchone()

        if row:
            # Update existing candidate
            candidate_id = row["id"]
            cursor.execute("""
                UPDATE candidates
                SET name = ?, phone = ?, resume_text = ?, file_path = ?
                WHERE id = ?
            """, (name, phone, resume_text, file_path, candidate_id))
        else:
            # Insert new candidate
            cursor.execute("""
                INSERT INTO candidates (name, email, phone, resume_text, file_path)
                VALUES (?, ?, ?, ?, ?)
            """, (name, email, phone, resume_text, file_path))
            candidate_id = cursor.lastrowid

        conn.commit()
        return candidate_id

    except sqlite3.Error as e:
        print(f"Database error during candidate insertion: {e}")
        return -1
    finally:
        conn.close()


def get_all_candidates():
    """
    Queries and returns all candidate records from the database.

    Returns:
        list: A list of dict-like SQLite Row objects.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM candidates ORDER BY created_at DESC")
    rows = cursor.fetchall()
    conn.close()
    return rows


def delete_candidate(candidate_id: int) -> bool:
    """
    Deletes a candidate by their unique ID.

    Args:
        candidate_id (int): Unique identifier of the candidate.

    Returns:
        bool: True if candidate was deleted, False otherwise.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    success = False

    try:
        cursor.execute("DELETE FROM candidates WHERE id = ?", (candidate_id,))
        conn.commit()
        # check if at least one row was affected (deleted)
        success = cursor.rowcount > 0
    except sqlite3.Error as e:
        print(f"Database error during candidate deletion: {e}")
    finally:
        conn.close()

    return success
