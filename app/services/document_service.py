from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile

from app.core.config import settings
from app.services.document_parser import DocumentParser
from app.services.embedding_service import EmbeddingService
from app.services.text_chunker import TextChunk, TextChunker
from app.services.vector_store import VectorStore


class DocumentService:
    _text_chunker = TextChunker()

    @staticmethod
    async def save_file(file: UploadFile) -> Path:
        upload_dir = Path(settings.UPLOAD_DIR)
        upload_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        original_filename = file.filename or "document"
        extension = Path(original_filename).suffix.lower()
        stored_filename = f"{uuid4().hex}{extension}"

        destination = upload_dir / stored_filename

        try:
            with destination.open("wb") as buffer:
                while chunk := await file.read(1024 * 1024):
                    buffer.write(chunk)
        except Exception:
            destination.unlink(missing_ok=True)
            raise
        finally:
            await file.close()

        return destination

    @staticmethod
    def extract_text(file_path: Path) -> str:
        return DocumentParser.extract_text(file_path)

    @classmethod
    def create_chunks(
        cls,
        text: str,
    ) -> list[TextChunk]:
        return cls._text_chunker.split_text(text)

    @staticmethod
    def index_chunks(
        document_id: str,
        original_filename: str,
        stored_filename: str,
        chunks: list[TextChunk],
    ) -> int:
        embedding_service = EmbeddingService()
        vector_store = VectorStore()

        chunk_texts = [chunk.content for chunk in chunks]

        embeddings = embedding_service.create_embeddings(chunk_texts)

        return vector_store.store_document_chunks(
            document_id=document_id,
            original_filename=original_filename,
            stored_filename=stored_filename,
            chunks=chunks,
            embeddings=embeddings,
        )

    @staticmethod
    def get_document_statistics(
        text: str,
        chunk_count: int,
        indexed_chunk_count: int,
    ) -> dict[str, int]:
        return {
            "character_count": len(text),
            "word_count": len(text.split()),
            "line_count": len(text.splitlines()),
            "chunk_count": chunk_count,
            "indexed_chunk_count": indexed_chunk_count,
        }
