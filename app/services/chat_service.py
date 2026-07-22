from dataclasses import dataclass

from app.core.config import settings
from app.services.llm_service import LLMService
from app.services.search_service import SearchService
from app.services.vector_store import VectorSearchResult


class ChatServiceError(Exception):
    """Raised when a document question cannot be processed."""


@dataclass(frozen=True, slots=True)
class ChatAnswer:
    answer: str
    sources: list[VectorSearchResult]


class ChatService:
    def __init__(self) -> None:
        self._search_service = SearchService()
        self._llm_service = LLMService()
        self._retrieval_limit = settings.CHAT_RETRIEVAL_LIMIT
        self._minimum_similarity = settings.CHAT_MIN_SIMILARITY

    async def ask(
        self,
        document_id: str,
        question: str,
    ) -> ChatAnswer:
        cleaned_document_id = document_id.strip()
        cleaned_question = question.strip()

        if not cleaned_document_id:
            raise ChatServiceError("Document ID cannot be empty.")

        if not cleaned_question:
            raise ChatServiceError("Question cannot be empty.")

        document_exists = self._search_service.document_exists(
            document_id=cleaned_document_id,
        )

        if not document_exists:
            raise ChatServiceError("Document was not found in the vector store.")

        retrieved_chunks = self._search_service.search(
            document_id=cleaned_document_id,
            query=cleaned_question,
            limit=self._retrieval_limit,
        )

        relevant_chunks = [
            chunk
            for chunk in retrieved_chunks
            if chunk.similarity >= self._minimum_similarity
        ]

        if not relevant_chunks:
            return ChatAnswer(
                answer=(
                    "I couldn't find that information " "in the uploaded document."
                ),
                sources=[],
            )

        context_parts = [
            (f"[Source chunk {chunk.chunk_index}]\n" f"{chunk.content}")
            for chunk in relevant_chunks
        ]

        context = "\n\n---\n\n".join(context_parts)

        answer = await self._llm_service.answer(
            question=cleaned_question,
            context=context,
        )

        return ChatAnswer(
            answer=answer,
            sources=relevant_chunks,
        )
