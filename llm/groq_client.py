"""
Groq API client for LLM inference
"""
import os
from typing import List, Dict, Optional
from groq import Groq
import streamlit as st

from config.settings import GROQ_MODEL, TEMPERATURE, MAX_TOKENS


class GroqClient:
    """Client for Groq API interactions"""
    
    def __init__(self):
        # Get API key from secrets or environment
        api_key = self._get_api_key()
        
        if not api_key:
            raise ValueError("GROQ_API_KEY not found in secrets or environment variables")
        
        self.client = Groq(api_key=api_key)
        self.model = GROQ_MODEL
    
    def _get_api_key(self) -> Optional[str]:
        """Get API key from Streamlit secrets or environment"""
        # Try Streamlit secrets first
        try:
            if hasattr(st, 'secrets') and 'GROQ_API_KEY' in st.secrets:
                return st.secrets['GROQ_API_KEY']
        except:
            pass
        
        # Fallback to environment variable
        return os.getenv('GROQ_API_KEY')
    
    def generate_response(self, system_prompt: str, user_prompt: str, 
                         temperature: float = TEMPERATURE,
                         max_tokens: int = MAX_TOKENS) -> str:
        """
        Generate a response using Groq API
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            return response.choices[0].message.content
        
        except Exception as e:
            print(f"Error generating response: {e}")
            return f"Error: Unable to generate response. {str(e)}"
    
    def generate_with_history(self, messages: List[Dict[str, str]], 
                             temperature: float = TEMPERATURE,
                             max_tokens: int = MAX_TOKENS) -> str:
        """
        Generate response with conversation history
        messages: list of {"role": "user/assistant/system", "content": "..."}
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            return response.choices[0].message.content
        
        except Exception as e:
            print(f"Error generating response with history: {e}")
            return f"Error: Unable to generate response. {str(e)}"
    
    def check_api_key(self) -> bool:
        """Check if API key is valid"""
        try:
            # Try a simple API call
            self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": "test"}],
                max_tokens=5
            )
            return True
        except Exception as e:
            print(f"API key validation failed: {e}")
            return False
