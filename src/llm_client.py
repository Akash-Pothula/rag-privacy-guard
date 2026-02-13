"""Azure OpenAI LLM client."""

import os
from openai import AzureOpenAI
from src.config import Config


class LLMClient:
    """Client for interacting with Azure OpenAI."""
    
    def __init__(self):
        """Initialize the LLM client with Azure OpenAI credentials."""
        self.client = AzureOpenAI(
            api_version=Config.LLM_API_VERSION,
            azure_endpoint=Config.LLM_ENDPOINT,
            api_key=Config.AZURE_OPENAI_API_KEY,
        )
        self.model = Config.LLM_MODEL_NAME

    def generate_response(self, system_message: str, user_message: str) -> str:
        """
        Generate a response from the LLM.
        
        Args:
            system_message: System prompt defining the LLM's role
            user_message: User input/question
            
        Returns:
            str: LLM response content
        """
        response = self.client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_message}
            ],
            max_completion_tokens=16384,
            model=self.model,
        )
        return response.choices[0].message.content

    def generate_with_context(self, question: str, context: str) -> str:
        """
        Generate a response with retrieved context.
        
        Args:
            question: User question
            context: Retrieved context for answering the question
            
        Returns:
            str: LLM response based on context
        """
        system_message = "You are a helpful assistant. Answer the question based on the provided context."
        user_message = f"""Context:
{context}

Question: {question}

Answer:"""
        return self.generate_response(system_message, user_message)
