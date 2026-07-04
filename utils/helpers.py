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
