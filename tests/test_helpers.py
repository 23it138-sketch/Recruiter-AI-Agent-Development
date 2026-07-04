import unittest
from utils.helpers import is_valid_resume, extract_email, extract_phone

class TestHelpers(unittest.TestCase):
    """
    Test suite to verify that helper functions in utils/helpers.py
    work correctly with various input formats and edge cases.
    """

    def test_is_valid_resume_allowed_formats(self):
        """Verify that allowed resume formats (.pdf, .docx, .doc) are recognized (case-insensitive)."""
        self.assertTrue(is_valid_resume("john_doe_resume.pdf"))
        self.assertTrue(is_valid_resume("alice_smith_cv.docx"))
        self.assertTrue(is_valid_resume("bob_jones_portfolio.DOC"))

    def test_is_valid_resume_blocked_formats(self):
        """Verify that invalid resume formats (like executables or images) are blocked."""
        self.assertFalse(is_valid_resume("malicious_code.exe"))
        self.assertFalse(is_valid_resume("avatar_photo.png"))
        self.assertFalse(is_valid_resume(""))
        self.assertFalse(is_valid_resume(None))

    def test_extract_email_success(self):
        """Verify that a valid email address is successfully extracted from a block of text."""
        sample_text = "Contact me at candidate.email@domain.com or call tomorrow."
        self.assertEqual(extract_email(sample_text), "candidate.email@domain.com")

    def test_extract_email_missing(self):
        """Verify that 'unknown@email.com' is returned if no email is found in text."""
        sample_text = "No contact details provided in this summary."
        self.assertEqual(extract_email(sample_text), "unknown@email.com")

    def test_extract_phone_success_formats(self):
        """Verify that different standard phone number patterns are extracted correctly."""
        # Test international format
        self.assertEqual(extract_phone("My number is +1-123-456-7890."), "+1-123-456-7890")
        # Test standard domestic format
        self.assertEqual(extract_phone("Call me at (555) 019-9234"), "(555) 019-9234")

    def test_extract_phone_missing(self):
        """Verify that 'N/A' is returned if no phone number matches in text."""
        self.assertEqual(extract_phone("Email me at test@example.com"), "N/A")

if __name__ == "__main__":
    unittest.main()
