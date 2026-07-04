import os

def is_valid_resume(filename: str) -> bool:
    """
    Checks if an uploaded file has a valid resume extension.
    Allowed extensions: .pdf, .docx, .doc

    Args:
        filename (str): The name of the file to check.

    Returns:
        bool: True if the file extension is allowed, False otherwise.
    """
    # 1. Ensure the filename is not empty or None
    if not filename:
        return False

    # 2. Extract the file extension (e.g., '.pdf') and convert it to lowercase
    _, ext = os.path.splitext(filename)
    ext = ext.lower()

    # 3. Check if the extension is in our list of allowed extensions
    allowed_extensions = {".pdf", ".docx", ".doc"}
    return ext in allowed_extensions


def extract_email(text: str) -> str:
    """
    Uses regular expressions to extract the first email address found in the text.

    Args:
        text (str): Extracted resume text.

    Returns:
        str: Extracted email or 'unknown@email.com' if not found.
    """
    import re
    email_pattern = r'[\w\.-]+@[\w\.-]+\.\w+'
    match = re.search(email_pattern, text)
    return match.group(0) if match else "unknown@email.com"


def extract_phone(text: str) -> str:
    """
    Uses regular expressions to extract the first phone number found in the text.
    Matches standard international and domestic formats.

    Args:
        text (str): Extracted resume text.

    Returns:
        str: Extracted phone number or 'N/A' if not found.
    """
    import re
    # Matches standard numbers like: +1-123-456-7890, (123) 456-7890, 123-456-7890, etc.
    phone_pattern = r'\+?(?:\d{1,3}[- ]?)?\(?\d{3}\)?[- ]?\d{3}[- ]?\d{4}'
    match = re.search(phone_pattern, text)
    return match.group(0) if match else "N/A"


def extract_entities_spacy(text: str) -> dict:
    """
    Uses spaCy NLP library to extract named entities (Organizations, Persons, Locations)
    from candidate resume text.
    
    Args:
        text (str): Resume text.
        
    Returns:
        dict: Lists of extracted entities categorized by label.
    """
    import spacy
    
    try:
        # Load the downloaded english language pipeline
        nlp = spacy.load("en_core_web_sm")
        doc = nlp(text)
        
        # Pull specific entity labels (limit to top 5 unique names per class to avoid dashboard clutter)
        orgs = list(set([ent.text for ent in doc.ents if ent.label_ == "ORG"]))[:5]
        people = list(set([ent.text for ent in doc.ents if ent.label_ == "PERSON"]))[:5]
        gpe = list(set([ent.text for ent in doc.ents if ent.label_ in ("GPE", "LOC")]))[:5]
        
        return {
            "organizations": orgs,
            "people": people,
            "locations": gpe
        }
    except Exception as e:
        print(f"spaCy NLP extraction failed: {e}")
        return {
            "organizations": [],
            "people": [],
            "locations": []
        }
