from io import BytesIO
from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient


def test_chat_returns_grounded_answer(client: TestClient) -> None:
    upload_response = client.post(
        "/api/v1/documents/upload",
        files={
            "file": (
                "sample.txt",
                BytesIO(b"FastAPI is a Python framework for building web APIs."),
                "text/plain",
            )
        },
    )

    assert upload_response.status_code == 201

    document_id = upload_response.json()["document_id"]

    with patch(
        "app.services.llm_service.LLMService.answer",
        new=AsyncMock(return_value="FastAPI is used for building web APIs."),
    ):
        response = client.post(
            "/api/v1/chat",
            json={
                "document_id": document_id,
                "question": "What is FastAPI used for?",
            },
        )

    assert response.status_code == 200

    body = response.json()

    assert body["status"] == "success"
    assert body["document_id"] == document_id
    assert body["question"] == "What is FastAPI used for?"
    assert body["answer"] == "FastAPI is used for building web APIs."
    assert body["used_chunks"] >= 1
    assert len(body["sources"]) >= 1
