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


def insert_job(title: str, description: str, skills_required: str = None) -> int:
    """
    Inserts a new job description profile into the jobs table.

    Args:
        title (str): Job role title.
        description (str): Full text of job description.
        skills_required (str, optional): Key skills requested.

    Returns:
        int: The ID of the inserted job profile.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO jobs (title, description, skills_required)
            VALUES (?, ?, ?)
        """, (title, description, skills_required))
        conn.commit()
        return cursor.lastrowid
    except sqlite3.Error as e:
        print(f"Database error during job insertion: {e}")
        return -1
    finally:
        conn.close()


def insert_match(candidate_id: int, job_id: int, match_score: float, ai_evaluation: str, generated_questions: list) -> int:
    """
    Inserts or updates an AI evaluation score and questions matching 
    a candidate to a specific job description.

    Args:
        candidate_id (int): Database ID of candidate.
        job_id (int): Database ID of job description.
        match_score (float): Computed AI fit percentage.
        ai_evaluation (str): Text assessment.
        generated_questions (list): Tailored interview questions.

    Returns:
        int: The ID of the inserted or updated match record.
    """
    import json
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Serialize questions list to JSON string for DB storage
    questions_json = json.dumps(generated_questions)

    try:
        # Check if matching record already exists
        cursor.execute("""
            SELECT id FROM matches 
            WHERE candidate_id = ? AND job_id = ?
        """, (candidate_id, job_id))
        row = cursor.fetchone()

        if row:
            match_id = row["id"]
            cursor.execute("""
                UPDATE matches
                SET match_score = ?, ai_evaluation = ?, generated_questions = ?, matched_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (match_score, ai_evaluation, questions_json, match_id))
        else:
            cursor.execute("""
                INSERT INTO matches (candidate_id, job_id, match_score, ai_evaluation, generated_questions)
                VALUES (?, ?, ?, ?, ?)
            """, (candidate_id, job_id, match_score, ai_evaluation, questions_json))
            match_id = cursor.lastrowid

        conn.commit()
        return match_id

    except sqlite3.Error as e:
        print(f"Database error during match insertion: {e}")
        return -1
    finally:
        conn.close()


def get_matches_for_job(job_id: int) -> list:
    """
    Queries and returns all candidate matching records for a given job.
    Joins candidate details for UI display, sorting by match score descending.

    Args:
        job_id (int): Database ID of the target job description.

    Returns:
        list: SQLite Row list containing candidate profiles and match scores.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT 
            m.id as match_id,
            m.match_score,
            m.ai_evaluation,
            m.generated_questions,
            m.matched_at,
            c.id as candidate_id,
            c.name as candidate_name,
            c.email as candidate_email,
            c.phone as candidate_phone
        FROM matches m
        JOIN candidates c ON m.candidate_id = c.id
        WHERE m.job_id = ?
        ORDER BY m.match_score DESC
    """, (job_id,))
    rows = cursor.fetchall()
    conn.close()
    return rows
