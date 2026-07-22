from dataclasses import dataclass
from pathlib import Path
from typing import Any, cast

import chromadb
from chromadb.api.models.Collection import Collection

from app.core.config import settings
from app.services.text_chunker import TextChunk


@dataclass(frozen=True, slots=True)
class VectorSearchResult:
    chunk_index: int
    content: str
    similarity: float
    original_filename: str
    stored_filename: str


class VectorStoreError(Exception):
    """Raised when vector storage operations fail."""


class VectorStore:
    def __init__(self) -> None:
        vector_store_path = Path(settings.VECTOR_STORE_DIR)

        vector_store_path.mkdir(
            parents=True,
            exist_ok=True,
        )

        try:
            self._client = chromadb.PersistentClient(
                path=str(vector_store_path),
            )

            self._collection: Collection = self._client.get_or_create_collection(
                name=settings.VECTOR_COLLECTION_NAME,
                metadata={
                    "description": ("DocuMindAI document chunks"),
                    "hnsw:space": "cosine",
                },
            )
        except Exception as error:
            raise VectorStoreError(
                f"Failed to initialize vector store: {error}"
            ) from error

    def store_document_chunks(
        self,
        document_id: str,
        original_filename: str,
        stored_filename: str,
        chunks: list[TextChunk],
        embeddings: list[list[float]],
    ) -> int:
        if not chunks:
            raise VectorStoreError("Cannot store an empty chunk list.")

        if len(chunks) != len(embeddings):
            raise VectorStoreError("Chunk count does not match embedding count.")

        ids = [f"{document_id}:{chunk.index}" for chunk in chunks]

        documents = [chunk.content for chunk in chunks]

        metadatas: list[dict[str, str | int]] = [
            {
                "document_id": document_id,
                "original_filename": original_filename,
                "stored_filename": stored_filename,
                "chunk_index": chunk.index,
                "character_count": chunk.character_count,
            }
            for chunk in chunks
        ]

        try:
            self._collection.upsert(
                ids=ids,
                documents=documents,
                embeddings=cast(
                    Any,
                    embeddings,
                ),
                metadatas=cast(
                    Any,
                    metadatas,
                ),
            )
        except Exception as error:
            raise VectorStoreError(
                f"Failed to store document chunks: {error}"
            ) from error

        return len(chunks)

    def search_document(
        self,
        document_id: str,
        query_embedding: list[float],
        limit: int,
    ) -> list[VectorSearchResult]:
        if not document_id.strip():
            raise VectorStoreError("Document ID cannot be empty.")

        if not query_embedding:
            raise VectorStoreError("Query embedding cannot be empty.")

        if limit <= 0:
            raise VectorStoreError("Search limit must be greater than zero.")

        try:
            response = self._collection.query(
                query_embeddings=cast(
                    Any,
                    [query_embedding],
                ),
                n_results=limit,
                where={
                    "document_id": document_id,
                },
                include=[
                    "documents",
                    "metadatas",
                    "distances",
                ],
            )
        except Exception as error:
            raise VectorStoreError(
                f"Failed to search document vectors: {error}"
            ) from error

        documents = self._first_result_list(response.get("documents"))
        metadatas = self._first_result_list(response.get("metadatas"))
        distances = self._first_result_list(response.get("distances"))

        results: list[VectorSearchResult] = []

        for document, metadata, distance in zip(
            documents,
            metadatas,
            distances,
            strict=False,
        ):
            if not isinstance(document, str):
                continue

            if not isinstance(metadata, dict):
                continue

            if not isinstance(
                distance,
                int | float,
            ):
                continue

            numeric_distance = float(distance)

            similarity = max(
                0.0,
                min(
                    1.0,
                    1.0 - numeric_distance,
                ),
            )

            results.append(
                VectorSearchResult(
                    chunk_index=int(
                        metadata.get(
                            "chunk_index",
                            0,
                        )
                    ),
                    content=document,
                    similarity=round(
                        similarity,
                        4,
                    ),
                    original_filename=str(
                        metadata.get(
                            "original_filename",
                            "",
                        )
                    ),
                    stored_filename=str(
                        metadata.get(
                            "stored_filename",
                            "",
                        )
                    ),
                )
            )

        return results

    def document_exists(
        self,
        document_id: str,
    ) -> bool:
        try:
            result = self._collection.get(
                where={
                    "document_id": document_id,
                },
                limit=1,
                include=[],
            )
        except Exception as error:
            raise VectorStoreError(
                f"Failed to check document existence: {error}"
            ) from error

        ids = result.get(
            "ids",
            [],
        )

        return bool(ids)

    def delete_document(
        self,
        document_id: str,
    ) -> None:
        try:
            self._collection.delete(
                where={
                    "document_id": document_id,
                },
            )
        except Exception as error:
            raise VectorStoreError(
                f"Failed to delete document vectors: {error}"
            ) from error

    @staticmethod
    def _first_result_list(
        value: Any,
    ) -> list[Any]:
        if not isinstance(value, list):
            return []

        if not value:
            return []

        first_item = value[0]

        if not isinstance(first_item, list):
            return []

        return first_item
