"""Gemini API client wrapper.

Provides a clean interface to the Google Gemini API.
The rest of the application should use this module rather than
importing the google-genai SDK directly.
"""
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class GeminiClient:
    """Wrapper around the Google Gemini API."""
    
    def __init__(self, api_key: str = None, model: str = None):
        from config import GEMINI_API_KEY, GEMINI_MODEL
        self._api_key = api_key or GEMINI_API_KEY
        self._model = model or GEMINI_MODEL
        self._client = None
        self._available = False
        self._init_client()
    
    def _init_client(self):
        if not self._api_key:
            logger.info("No Gemini API key provided. AI features disabled.")
            return
        try:
            from google import genai
            self._client = genai.Client(api_key=self._api_key)
            self._available = True
            logger.info("Gemini client initialized successfully.")
        except Exception as e:
            logger.warning(f"Failed to initialize Gemini client: {e}")
            self._available = False
    
    @property
    def is_available(self) -> bool:
        return self._available
    
    def generate(self, prompt: str, system_instruction: str = None) -> Optional[str]:
        """Generate text from a prompt. Returns None if unavailable or on error."""
        if not self._available:
            return None
        try:
            from google.genai import types
            config = None
            if system_instruction:
                config = types.GenerateContentConfig(
                    system_instruction=system_instruction
                )
            response = self._client.models.generate_content(
                model=self._model,
                contents=prompt,
                config=config
            )
            return response.text
        except Exception as e:
            logger.error(f"Gemini generation error: {e}")
            return None
    
    def chat(self, messages: list[dict], system_instruction: str = None) -> Optional[str]:
        """Send a chat conversation. messages is a list of {role, content} dicts.
        Returns the assistant's response text or None."""
        if not self._available:
            return None
        try:
            from google.genai import types
            # Build the contents for the API
            # Convert our simple format to Gemini format
            contents = []
            for msg in messages:
                role = "user" if msg["role"] == "user" else "model"
                contents.append(types.Content(
                    role=role,
                    parts=[types.Part(text=msg["content"])]
                ))
            
            config = None
            if system_instruction:
                config = types.GenerateContentConfig(
                    system_instruction=system_instruction
                )
            
            response = self._client.models.generate_content(
                model=self._model,
                contents=contents,
                config=config
            )
            return response.text
        except Exception as e:
            logger.error(f"Gemini chat error: {e}")
            return None


# Singleton instance
_instance: Optional[GeminiClient] = None

def get_gemini_client() -> GeminiClient:
    global _instance
    if _instance is None:
        _instance = GeminiClient()
    return _instance
