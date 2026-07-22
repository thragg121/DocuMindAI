from threading import Lock

from sentence_transformers import SentenceTransformer

from app.core.config import settings


class EmbeddingServiceError(Exception):
    """Raised when local embeddings cannot be generated."""


class EmbeddingService:
    _model: SentenceTransformer | None = None
    _model_lock = Lock()

    def __init__(self) -> None:
        self._model_name = settings.EMBEDDING_MODEL
        self._batch_size = settings.EMBEDDING_BATCH_SIZE

    def create_embeddings(
        self,
        texts: list[str],
    ) -> list[list[float]]:
        if not texts:
            raise EmbeddingServiceError(
                "Cannot create embeddings for an empty text list."
            )

        cleaned_texts = [text.strip() for text in texts]

        if any(not text for text in cleaned_texts):
            raise EmbeddingServiceError("Cannot create an embedding for empty text.")

        try:
            model = self._get_model()

            embeddings = model.encode(
                cleaned_texts,
                batch_size=self._batch_size,
                show_progress_bar=False,
                normalize_embeddings=True,
                convert_to_numpy=True,
            )
        except Exception as error:
            raise EmbeddingServiceError(
                f"Failed to create local embeddings: {error}"
            ) from error

        if len(embeddings) != len(cleaned_texts):
            raise EmbeddingServiceError(
                "Embedding result size does not match input size."
            )

        return [embedding.astype(float).tolist() for embedding in embeddings]

    @classmethod
    def _get_model(cls) -> SentenceTransformer:
        if cls._model is not None:
            return cls._model

        with cls._model_lock:
            if cls._model is None:
                try:
                    cls._model = SentenceTransformer(settings.EMBEDDING_MODEL)
                except Exception as error:
                    raise EmbeddingServiceError(
                        "Failed to load the local embedding model: " f"{error}"
                    ) from error

        return cls._model
