from typing import Any, Type, Optional
from langchain_groq import ChatGroq
from pydantic import BaseModel
from app.core.config import settings

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
        Unified completion wrapper using LangChain's ChatGroq client.
        Natively handles structured output generation via with_structured_output().
        """
        if not settings.GROQ_API_KEY:
            raise ValueError("GROQ_API_KEY is not set.")

        llm = ChatGroq(
            api_key = settings.GROQ_API_KEY,
            model_name = model,
            temperature = temperature
        )

        messages = [
            ("system", system_prompt),
            ("human", user_prompt)
        ]

        if response_model:
            structured_llm = llm.with_structured_output(response_model)
            return structured_llm.invoke(messages)
        
        response = llm.invoke(messages)
        return response.content