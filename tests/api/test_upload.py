from io import BytesIO

from fastapi.testclient import TestClient


def test_upload_txt_document(client: TestClient) -> None:
    file_content = b"DocuMindAI test document."

    response = client.post(
        "/api/v1/documents/upload",
        files={
            "file": (
                "sample.txt",
                BytesIO(file_content),
                "text/plain",
            )
        },
    )

    assert response.status_code == 201

    body = response.json()

    assert body["status"] == "success"
    assert body["original_filename"] == "sample.txt"
    assert body["statistics"]["chunk_count"] >= 1
    assert body["statistics"]["indexed_chunk_count"] >= 1
