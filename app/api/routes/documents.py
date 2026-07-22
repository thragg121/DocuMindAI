from fastapi import (
    APIRouter,
    File,
    HTTPException,
    UploadFile,
    status,
)

from app.schemas.documents import (
    DocumentChunkPreview,
    DocumentStatistics,
    DocumentUploadResponse,
)
from app.services.document_parser import DocumentParsingError
from app.services.document_service import DocumentService
from app.services.embedding_service import EmbeddingServiceError
from app.services.text_chunker import TextChunkingError
from app.services.vector_store import (
    VectorStore,
    VectorStoreError,
)
from app.utils.file_validation import validate_extension

router = APIRouter(
    prefix="/documents",
    tags=["Documents"],
)


@router.post(
    "/upload",
    response_model=DocumentUploadResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_document(
    file: UploadFile = File(...),
) -> DocumentUploadResponse:
    original_filename = file.filename or ""

    if not original_filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The uploaded file must have a filename.",
        )

    if not validate_extension(original_filename):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=("Unsupported file type. " "Allowed types: PDF, DOCX and TXT."),
        )

    saved_path = await DocumentService.save_file(file)
    document_id = saved_path.stem

    try:
        extracted_text = DocumentService.extract_text(saved_path)

        chunks = DocumentService.create_chunks(extracted_text)

        indexed_chunk_count = DocumentService.index_chunks(
            document_id=document_id,
            original_filename=original_filename,
            stored_filename=saved_path.name,
            chunks=chunks,
        )
    except (
        DocumentParsingError,
        TextChunkingError,
        EmbeddingServiceError,
        VectorStoreError,
    ) as error:
        saved_path.unlink(missing_ok=True)

        try:
            VectorStore().delete_document(
                document_id=document_id,
            )
        except VectorStoreError:
            pass

        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(error),
        ) from error

    statistics_data = DocumentService.get_document_statistics(
        text=extracted_text,
        chunk_count=len(chunks),
        indexed_chunk_count=indexed_chunk_count,
    )

    statistics = DocumentStatistics(
        character_count=statistics_data["character_count"],
        word_count=statistics_data["word_count"],
        line_count=statistics_data["line_count"],
        chunk_count=statistics_data["chunk_count"],
        indexed_chunk_count=statistics_data["indexed_chunk_count"],
    )

    preview_length = 500
    text_preview = extracted_text[:preview_length]

    if len(extracted_text) > preview_length:
        text_preview += "..."

    first_chunk = chunks[0]

    return DocumentUploadResponse(
        status="success",
        document_id=document_id,
        original_filename=original_filename,
        stored_filename=saved_path.name,
        content_type=file.content_type,
        saved_to=str(saved_path),
        text_preview=text_preview,
        chunk_preview=DocumentChunkPreview(
            index=first_chunk.index,
            content=first_chunk.content,
            character_count=first_chunk.character_count,
        ),
        statistics=statistics,
    )
