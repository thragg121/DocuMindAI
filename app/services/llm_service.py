from __future__ import annotations

from typing import Any

import httpx

from app.core.config import settings


class LLMServiceError(Exception):
    """Raised when the local language model cannot generate an answer."""


class LLMService:
    def __init__(self) -> None:
        self._base_url = settings.OLLAMA_URL.rstrip("/")
        self._model = settings.OLLAMA_MODEL

    async def answer(
        self,
        question: str,
        context: str,
    ) -> str:
        cleaned_question = question.strip()
        cleaned_context = context.strip()

        if not cleaned_question:
            raise LLMServiceError("Question cannot be empty.")

        if not cleaned_context:
            return "I couldn't find that information " "in the uploaded document."

        system_prompt = (
            "You are DocuMindAI, a document question-answering "
            "assistant.\n\n"
            "Follow these rules:\n"
            "1. Answer only from the provided document context.\n"
            "2. Do not use outside knowledge.\n"
            "3. Do not invent names, dates, amounts, obligations, "
            "or conclusions.\n"
            "4. If the context does not contain enough information, "
            "say exactly: \"I couldn't find that information in the "
            'uploaded document."\n'
            "5. Answer in the same language as the user's question.\n"
            "6. Be concise but include all relevant details.\n\n"
            f"DOCUMENT CONTEXT:\n{cleaned_context}"
        )

        payload = {
            "model": self._model,
            "stream": False,
            "messages": [
                {
                    "role": "system",
                    "content": system_prompt,
                },
                {
                    "role": "user",
                    "content": cleaned_question,
                },
            ],
            "options": {
                "temperature": 0.1,
            },
        }

        try:
            async with httpx.AsyncClient(
                timeout=httpx.Timeout(180.0),
            ) as client:
                response = await client.post(
                    f"{self._base_url}/api/chat",
                    json=payload,
                )

            response.raise_for_status()
            data: Any = response.json()

        except httpx.ConnectError as error:
            raise LLMServiceError(
                "Could not connect to Ollama. " "Make sure Ollama is running."
            ) from error

        except httpx.TimeoutException as error:
            raise LLMServiceError(
                "Ollama did not respond before the timeout."
            ) from error

        except httpx.HTTPStatusError as error:
            raise LLMServiceError(
                "Ollama returned an HTTP error: " f"{error.response.status_code}."
            ) from error

        except ValueError as error:
            raise LLMServiceError("Ollama returned invalid JSON.") from error

        except Exception as error:
            raise LLMServiceError(f"Failed to generate an answer: {error}") from error

        if not isinstance(data, dict):
            raise LLMServiceError("Ollama returned an unexpected response.")

        message = data.get("message")

        if not isinstance(message, dict):
            raise LLMServiceError("Ollama response does not contain a message.")

        content = message.get("content")

        if not isinstance(content, str) or not content.strip():
            raise LLMServiceError("Ollama returned an empty answer.")

        return content.strip()
