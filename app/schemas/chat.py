from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    document_id: str = Field(
        min_length=1,
        description="Identifier returned after document upload.",
    )
    question: str = Field(
        min_length=2,
        max_length=4000,
        description="Question about the uploaded document.",
    )


class ChatSource(BaseModel):
    chunk_index: int = Field(ge=0)
    similarity: float = Field(
        ge=0.0,
        le=1.0,
    )
    content_preview: str
    original_filename: str


class ChatResponse(BaseModel):
    status: str
    document_id: str
    question: str
    answer: str
    used_chunks: int = Field(ge=0)
    sources: list[ChatSource]
