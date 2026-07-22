from fastapi import (
    APIRouter,
    HTTPException,
    status,
)

from app.schemas.chat import (
    ChatRequest,
    ChatResponse,
    ChatSource,
)
from app.services.chat_service import (
    ChatService,
    ChatServiceError,
)
from app.services.embedding_service import (
    EmbeddingServiceError,
)
from app.services.llm_service import LLMServiceError
from app.services.vector_store import VectorStoreError

router = APIRouter(
    prefix="/chat",
    tags=["Chat"],
)


@router.post(
    "",
    response_model=ChatResponse,
)
async def chat(
    request: ChatRequest,
) -> ChatResponse:
    service = ChatService()

    try:
        result = await service.ask(
            document_id=request.document_id,
            question=request.question,
        )
    except ChatServiceError as error:
        error_message = str(error)

        if "not found" in error_message.lower():
            response_status = status.HTTP_404_NOT_FOUND
        else:
            response_status = status.HTTP_422_UNPROCESSABLE_ENTITY

        raise HTTPException(
            status_code=response_status,
            detail=error_message,
        ) from error
    except (
        EmbeddingServiceError,
        VectorStoreError,
        LLMServiceError,
    ) as error:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(error),
        ) from error

    sources = [
        ChatSource(
            chunk_index=source.chunk_index,
            similarity=source.similarity,
            content_preview=(
                source.content[:300] + "..."
                if len(source.content) > 300
                else source.content
            ),
            original_filename=source.original_filename,
        )
        for source in result.sources
    ]

    return ChatResponse(
        status="success",
        document_id=request.document_id.strip(),
        question=request.question.strip(),
        answer=result.answer,
        used_chunks=len(sources),
        sources=sources,
    )
