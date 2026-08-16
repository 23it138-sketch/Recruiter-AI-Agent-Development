import logging
from typing import Dict, Any, Optional
from gemini_client import get_gemini_client

logger = logging.getLogger(__name__)

class ChatAgent:
    """AI recruitment assistant."""
    
    def __init__(self):
        self.client = get_gemini_client()
        self.history = []
        
    @property
    def is_available(self) -> bool:
        return self.client.is_available
        
    def get_system_instruction(self, context: Optional[Dict[str, Any]] = None) -> str:
        """Build the system instruction with recruitment expertise and context."""
        base_instruction = (
            "You are an expert AI recruitment assistant. Your goal is to help recruiters by: "
            "analyzing candidate fit, suggesting interview questions, comparing candidates, "
            "identifying skill gaps, and providing hiring recommendations. "
            "Be professional, objective, and insightful."
        )
        
        if not context:
            return base_instruction
            
        context_parts = []
        
        if "job" in context:
            job = context["job"]
            context_parts.append(
                f"Job Details:\nTitle: {job.get('title')}\n"
                f"Requirements: {', '.join(job.get('requirements', []))}\n"
                f"Description: {job.get('description', '')}"
            )
            
        if "resume" in context:
            resume = context["resume"]
            # Assuming ResumeData or dict
            skills = resume.skills if hasattr(resume, "skills") else resume.get("skills", [])
            experience = resume.experience if hasattr(resume, "experience") else resume.get("experience", [])
            context_parts.append(
                f"Candidate Details:\nSkills: {', '.join(skills)}\n"
                f"Experience: {', '.join(experience)}"
            )
            
        if context_parts:
            additional_context = "\n\nContext Information:\n" + "\n\n".join(context_parts)
            return base_instruction + additional_context
            
        return base_instruction
        
    def chat(self, message: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Send a message to the AI assistant."""
        if not self.is_available:
            return "AI features are currently unavailable. Please provide a GEMINI_API_KEY to enable the AI recruitment assistant."
            
        self.history.append({"role": "user", "content": message})
        
        system_instruction = self.get_system_instruction(context)
        
        response_text = self.client.chat(messages=self.history, system_instruction=system_instruction)
        
        if response_text:
            self.history.append({"role": "model", "content": response_text})
            return response_text
        else:
            # Revert the last user message if generation failed
            self.history.pop()
            return "Sorry, I encountered an error while processing your request. Please try again."
            
    def clear_history(self) -> None:
        """Clear the chat history."""
        self.history = []
