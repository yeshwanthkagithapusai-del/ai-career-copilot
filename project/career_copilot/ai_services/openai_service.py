"""
Base AI service - provides a modular interface for LLM integration.
Supports OpenAI API with graceful fallback to heuristic analysis.
"""
import json
import os
from django.conf import settings


class AIService:
    """Modular AI service that supports OpenAI with fallback to heuristic logic."""
    
    def __init__(self):
        self.api_key = settings.OPENAI_API_KEY
        self.model = settings.OPENAI_MODEL
        self._client = None
    
    @property
    def client(self):
        """Lazily initialize OpenAI client."""
        if self._client is None and self.api_key:
            try:
                from openai import OpenAI
                self._client = OpenAI(api_key=self.api_key)
            except Exception:
                self._client = None
        return self._client
    
    @property
    def is_available(self):
        """Check if OpenAI API is configured and available."""
        return self.client is not None
    
    def chat_completion(self, messages, temperature=0.7, max_tokens=2000):
        """
        Send a chat completion request to OpenAI.
        Returns the response text or None if unavailable.
        """
        if not self.is_available:
            return None
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            return response.choices[0].message.content
        except Exception:
            return None
    
    def chat_completion_json(self, messages, temperature=0.7, max_tokens=2000):
        """
        Send a chat completion request and parse JSON response.
        Returns parsed dict or None.
        """
        text = self.chat_completion(messages, temperature, max_tokens)
        if text is None:
            return None
        
        try:
            # Try to extract JSON from response
            text = text.strip()
            if text.startswith('```json'):
                text = text[7:]
            if text.startswith('```'):
                text = text[3:]
            if text.endswith('```'):
                text = text[:-3]
            text = text.strip()
            return json.loads(text)
        except (json.JSONDecodeError, Exception):
            return None
