"""Gemini LLM client wrapper using official google-genai SDK."""

import json
from typing import Any, TypeVar
from pydantic import BaseModel
import structlog

from app.config import settings

logger = structlog.get_logger(__name__)

T = TypeVar("T", bound=BaseModel)


class LLMClient:
    """Async Gemini client wrapper for text and structured JSON generation."""

    def __init__(self) -> None:
        self._client: Any = None
        self._initialized: bool = False

    def _get_client(self) -> Any:
        """Always create a fresh client using current settings (avoids stale cached values)."""
        if settings.llm_api_key:
            from google import genai
            return genai.Client(api_key=settings.llm_api_key)
        logger.warning("no_llm_api_key_configured_using_mock_fallback")
        return None

    async def generate_text(
        self,
        prompt: str,
        system_instruction: str | None = None,
        temperature: float = 0.7,
    ) -> str:
        """Generate text using Gemini model."""
        client = self._get_client()
        if not client:
            return "Mock response: LLM API key is not configured."

        try:
            from google.genai import types

            config = types.GenerateContentConfig(
                temperature=temperature,
                system_instruction=system_instruction,
            )

            response = await client.aio.models.generate_content(
                model=settings.llm_model,
                contents=prompt,
                config=config,
            )
            return response.text or ""
        except Exception as e:
            logger.error("gemini_generate_text_failed", error=str(e))
            raise

    async def generate_structured(
        self,
        prompt: str,
        response_schema: type[T],
        system_instruction: str | None = None,
        temperature: float = 0.2,
    ) -> T:
        """Generate structured data parsed into a Pydantic model."""
        client = self._get_client()
        if not client:
            raise ValueError("LLM API key is not configured.")

        try:
            from google.genai import types

            config = types.GenerateContentConfig(
                temperature=temperature,
                system_instruction=system_instruction,
                response_mime_type="application/json",
                response_schema=response_schema,
            )

            response = await client.aio.models.generate_content(
                model=settings.llm_model,
                contents=prompt,
                config=config,
            )

            response_text = response.text or "{}"
            return response_schema.model_validate_json(response_text)
        except Exception as e:
            logger.error("gemini_generate_structured_failed", error=str(e))
            raise


# Singleton instance
llm_client = LLMClient()
