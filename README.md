# AI Recruiter Agent 💼🤖

An AI-powered recruitment assistant built using **Streamlit**, **LangChain**, and the **Google Gemini API**. This application helps recruiters upload candidate resumes (PDF/DOCX), parse and extract candidate details, store them in a local SQLite database, compare candidates to job descriptions, rank candidates, and generate tailored interview questions.

---

## 🚀 Key Features

*   **Resume Parsing**: Automatically extract candidate details (name, contact, skills, experience) from uploaded PDF and Word documents.
*   **Database Storage**: Persist candidate profiles, job descriptions, and matches using SQLite.
*   **Semantic Matching & Ranking**: Use Sentence Transformers and FAISS vector search to compare resume embeddings with job requirements and calculate matching scores.
*   **AI Assessment**: Leverage LangChain and Google Gemini to evaluate candidates and generate targeted interview questions.
*   **Recruiter Dashboard**: A clean, modern user interface built using Streamlit.

---

## 🛠️ Tech Stack

*   **Frontend & Dashboard**: Streamlit
*   **Backend & Orchestration**: Python, LangChain
*   **LLM API**: Google Gemini (via `langchain-google-genai`)
*   **NLP & Parsing**: spaCy, PyMuPDF (fitz), pdfplumber
*   **Vector Search & Embeddings**: FAISS, Sentence Transformers
*   **Database**: SQLite

---

## 📁 Project Structure

```text
Recruiter-AI-Agent/
│
├── app.py                 # Main Streamlit dashboard entry point
├── requirements.txt       # Project dependencies and libraries
├── README.md              # Project documentation
├── .env                   # Environment variables (Google Gemini API key) - IGNORED by git
├── .gitignore             # Config file telling Git what files to ignore
│
├── uploads/               # Directory for temporary uploaded files
├── resumes/               # Directory for storing processed/saved resumes
├── database/              # SQLite database storage directory
├── agents/                # AI logic and LangChain prompt templates
├── models/                # Custom data structures and schemas
├── pages/                 # Multi-page Streamlit dashboards
├── utils/                 # Document parsing and text utilities
└── tests/                 # Unit and integration tests
```

---

## ⚙️ Setup and Installation

### 1. Clone the repository
```bash
git clone <your-repository-url>
cd Recruiter-AI-Agent
```

### 2. Create and activate a Virtual Environment
**On Windows:**
```bash
py -m venv .venv
.venv\Scripts\activate
```
**On macOS/Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Create a file named `.env` in the root directory and add your Google Gemini API key:
```env
GEMINI_API_KEY="your_api_key_here"
```

### 5. Run the Application
```bash
streamlit run app.py
```
