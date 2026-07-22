from io import BytesIO

from fastapi.testclient import TestClient


def test_search_returns_results(client: TestClient) -> None:
    upload = client.post(
        "/api/v1/documents/upload",
        files={
            "file": (
                "sample.txt",
                BytesIO(b"Python is a programming language. FastAPI is used for APIs."),
                "text/plain",
            )
        },
    )

    assert upload.status_code == 201

    document_id = upload.json()["document_id"]

    response = client.post(
        "/api/v1/search",
        json={
            "document_id": document_id,
            "query": "FastAPI",
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert body["status"] == "success"
    assert body["result_count"] >= 1
    assert len(body["results"]) >= 1
