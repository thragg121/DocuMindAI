from pydantic import BaseModel, Field


class DocumentStatistics(BaseModel):
    character_count: int = Field(
        ge=0,
        description=("Number of characters extracted from the document."),
    )
    word_count: int = Field(
        ge=0,
        description=("Number of words extracted from the document."),
    )
    line_count: int = Field(
        ge=0,
        description=("Number of text lines extracted from the document."),
    )
    chunk_count: int = Field(
        ge=0,
        description=("Number of chunks created from the document."),
    )
    indexed_chunk_count: int = Field(
        ge=0,
        description=("Number of chunks stored in the vector database."),
    )


class DocumentChunkPreview(BaseModel):
    index: int = Field(
        ge=0,
        description=("Position of the chunk in the document."),
    )
    content: str
    character_count: int = Field(
        ge=0,
        description=("Number of characters in the chunk."),
    )


class DocumentUploadResponse(BaseModel):
    status: str
    document_id: str
    original_filename: str
    stored_filename: str
    content_type: str | None
    saved_to: str
    text_preview: str
    chunk_preview: DocumentChunkPreview
    statistics: DocumentStatistics
