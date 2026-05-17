from typing import Any, Dict, Type, Optional
from groq import Groq
import json
from pydantic import BaseModel

from app.core.config import settings
from app.observability.trace_logger import TraceLogger

# Initialize Groq client
client = Groq(api_key=settings.GROQ_API_KEY) if settings.GROQ_API_KEY else None

class LLMClient:
    @staticmethod
    def get_completion(
        system_prompt: str,
        user_prompt: str,
        model: str = "llama3-8b-8192",
        temperature: float = 0.0,
        response_model: Optional[Type[BaseModel]] = None
    ) -> Any:
        """
        Base wrapper for Groq completion.
        If response_model is provided, we force JSON output.
        """
        if not client:
            raise ValueError("GROQ_API_KEY is not set.")
            
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        kwargs = {
            "messages": messages,
            "model": model,
            "temperature": temperature,
        }
        
        if response_model:
            kwargs["response_format"] = {"type": "json_object"}
            
        response = client.chat.completions.create(**kwargs)
        content = response.choices[0].message.content
        
        if response_model:
            try:
                # Groq returns JSON string when response_format is json_object
                parsed = json.loads(content)
                return response_model(**parsed)
            except Exception as e:
                # Basic retry/fallback could go here, but for MVP we fail fast
                raise ValueError(f"Failed to parse LLM output into {response_model.__name__}: {e}\nContent: {content}")
        
        return content
