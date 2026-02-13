"""Configuration management for RAG Privacy Guard."""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Centralized configuration using environment variables."""
    
    # Azure OpenAI Configuration
    AZURE_OPENAI_API_KEY = os.environ.get("AZURE_OPENAI_API_KEY", "")
    LLM_ENDPOINT = os.environ.get("AZURE_OPENAI_ENDPOINT", "")
    LLM_API_VERSION = os.environ.get("AZURE_OPENAI_API_VERSION", "2024-12-01-preview")
    LLM_MODEL_NAME = os.environ.get("AZURE_OPENAI_MODEL_NAME", "gpt-4o")
    
    @classmethod
    def validate(cls) -> bool:
        """
        Validate that all required configuration is present.
        
        Returns:
            bool: True if configuration is valid, False otherwise
        """
        required_fields = [
            ("AZURE_OPENAI_API_KEY", cls.AZURE_OPENAI_API_KEY),
            ("AZURE_OPENAI_ENDPOINT", cls.LLM_ENDPOINT),
        ]
        
        missing = [field for field, value in required_fields if not value]
        
        if missing:
            print(f"Missing required configuration: {', '.join(missing)}")
            return False
        
        return True
