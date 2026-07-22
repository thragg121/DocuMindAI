from pydantic import BaseModel, Field


class DocumentSearchRequest(BaseModel):
    document_id: str = Field(
        min_length=1,
        description="Identifier returned after document upload.",
    )
    query: str = Field(
        min_length=2,
        max_length=2000,
        description="Semantic search query.",
    )
    limit: int = Field(
        default=5,
        ge=1,
        le=20,
        description="Maximum number of matching chunks.",
    )


class DocumentSearchResult(BaseModel):
    chunk_index: int = Field(
        ge=0,
        description="Position of the chunk in the document.",
    )
    content: str
    similarity: float = Field(
        ge=0.0,
        le=1.0,
        description="Semantic similarity score.",
    )
    original_filename: str
    stored_filename: str


class DocumentSearchResponse(BaseModel):
    status: str
    document_id: str
    query: str
    result_count: int = Field(ge=0)
    results: list[DocumentSearchResult]
