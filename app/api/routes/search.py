from fastapi import (
    APIRouter,
    HTTPException,
    status,
)

from app.schemas.search import (
    DocumentSearchRequest,
    DocumentSearchResponse,
    DocumentSearchResult,
)
from app.services.embedding_service import (
    EmbeddingServiceError,
)
from app.services.search_service import SearchService
from app.services.vector_store import VectorStoreError

router = APIRouter(
    prefix="/search",
    tags=["Search"],
)


@router.post(
    "",
    response_model=DocumentSearchResponse,
)
def search_document(
    request: DocumentSearchRequest,
) -> DocumentSearchResponse:
    search_service = SearchService()

    try:
        document_exists = search_service.document_exists(
            document_id=request.document_id,
        )

        if not document_exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=("Document was not found in the vector store."),
            )

        results = search_service.search(
            document_id=request.document_id,
            query=request.query,
            limit=request.limit,
        )
    except HTTPException:
        raise
    except (
        EmbeddingServiceError,
        VectorStoreError,
    ) as error:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(error),
        ) from error

    response_results = [
        DocumentSearchResult(
            chunk_index=result.chunk_index,
            content=result.content,
            similarity=result.similarity,
            original_filename=result.original_filename,
            stored_filename=result.stored_filename,
        )
        for result in results
    ]

    return DocumentSearchResponse(
        status="success",
        document_id=request.document_id,
        query=request.query.strip(),
        result_count=len(response_results),
        results=response_results,
    )
