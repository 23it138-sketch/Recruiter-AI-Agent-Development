import fitz  # PyMuPDF
import pdfplumber
import docx
import re
import os

def clean_text(text: str) -> str:
    """
    Cleans extracted text by removing extra whitespaces, newlines,
    and non-printable characters to prepare it for NLP analysis.

    Args:
        text (str): The raw text extracted from a document.

    Returns:
        str: The cleaned and normalized text.
    """
    if not text:
        return ""

    # 1. Replace multiple consecutive spaces/tabs with a single space
    cleaned = re.sub(r'[ \t]+', ' ', text)

    # 2. Replace multiple consecutive newlines with a single newline
    cleaned = re.sub(r'\n+', '\n', cleaned)

    # 3. Strip leading and trailing spaces from the entire text
    cleaned = cleaned.strip()

    return cleaned


def extract_text_from_pdf(pdf_path: str) -> str:
    """
    Opens a PDF file and extracts raw text from all pages using PyMuPDF.
    If PyMuPDF returns empty text, falls back to pdfplumber.

    Args:
        pdf_path (str): The absolute or relative path to the PDF file.

    Returns:
        str: Extracted and cleaned text from the PDF.
    """
    raw_text = []

    try:
        # 1. Try PyMuPDF (fitz) first
        doc = fitz.open(pdf_path)
        for page_num in range(len(doc)):
            page = doc[page_num]
            page_text = page.get_text()
            if page_text:
                raw_text.append(page_text)
        doc.close()
    except Exception as e:
        print(f"PyMuPDF failed on {pdf_path}, trying pdfplumber: {e}")

    # 2. Fallback to pdfplumber if PyMuPDF returned no text (e.g. for certain encoding tables)
    if not "".join(raw_text).strip():
        raw_text = []
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        raw_text.append(page_text)
        except Exception as e:
            print(f"pdfplumber failed on {pdf_path}: {e}")

    full_text = "\n".join(raw_text)
    return clean_text(full_text)


def extract_text_from_docx(docx_path: str) -> str:
    """
    Opens a Word document (.docx) and extracts clean text from all paragraphs.

    Args:
        docx_path (str): Path to the .docx file.

    Returns:
        str: Cleaned text from the Word document.
    """
    raw_text = []
    try:
        doc = docx.Document(docx_path)
        for para in doc.paragraphs:
            if para.text:
                raw_text.append(para.text)
    except Exception as e:
        print(f"Error opening or reading DOCX at {docx_path}: {e}")
        return ""

    full_text = "\n".join(raw_text)
    return clean_text(full_text)


def extract_text(file_path: str) -> str:
    """
    General entry point to extract text from a file based on its file extension.

    Args:
        file_path (str): Path to the document.

    Returns:
        str: Cleaned text of the document.
    """
    _, ext = os.path.splitext(file_path)
    ext = ext.lower()

    if ext == ".pdf":
        return extract_text_from_pdf(file_path)
    elif ext in (".docx", ".doc"):
        return extract_text_from_docx(file_path)
    else:
        print(f"Unsupported document format: {ext}")
        return ""


def extract_metadata(text: str) -> dict:
    """
    Extracts basic metadata metrics from clean document text.
    Assumes an average of 350 words per page for page count estimation.

    Args:
        text (str): The cleaned text of the document.

    Returns:
        dict: A dictionary containing word count, character count, and estimated page count.
    """
    import math

    if not text:
        return {
            "word_count": 0,
            "char_count": 0,
            "estimated_pages": 0
        }

    # 1. Split text on whitespaces to get all words and count them
    words = text.split()
    word_count = len(words)

    # 2. Count the characters including spaces
    char_count = len(text)

    # 3. Estimate page count (350 words per page, rounding up to nearest integer)
    # Using math.ceil to round up (e.g., ceil(1.2) = 2)
    estimated_pages = math.ceil(word_count / 350) if word_count > 0 else 0

    return {
        "word_count": word_count,
        "char_count": char_count,
        "estimated_pages": estimated_pages
    }
