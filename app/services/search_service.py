from app.services.embedding_service import EmbeddingService
from app.services.vector_store import (
    VectorSearchResult,
    VectorStore,
)


class SearchService:
    def __init__(self) -> None:
        self._embedding_service = EmbeddingService()
        self._vector_store = VectorStore()

    def document_exists(
        self,
        document_id: str,
    ) -> bool:
        return self._vector_store.document_exists(
            document_id=document_id,
        )

    def search(
        self,
        document_id: str,
        query: str,
        limit: int,
    ) -> list[VectorSearchResult]:
        cleaned_query = query.strip()

        query_embeddings = self._embedding_service.create_embeddings([cleaned_query])

        query_embedding = query_embeddings[0]

        return self._vector_store.search_document(
            document_id=document_id,
            query_embedding=query_embedding,
            limit=limit,
        )
