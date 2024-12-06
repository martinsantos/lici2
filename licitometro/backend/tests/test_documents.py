import pytest
from fastapi import UploadFile
from io import BytesIO
from backend.document_service.models import Document

@pytest.fixture
def test_file():
    content = b"test file content"
    return {
        "content": content,
        "filename": "test.txt",
        "content_type": "text/plain",
        "size": len(content)
    }

async def test_upload_document(client, test_user_token, test_file):
    # Create file-like object
    file = BytesIO(test_file["content"])
    files = {"file": (test_file["filename"], file, test_file["content_type"])}
    
    response = await client.post(
        f"{settings.api_v1_prefix}/documents/",
        files=files,
        headers={"Authorization": f"Bearer {test_user_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["original_filename"] == test_file["filename"]
    assert data["content_type"] == test_file["content_type"]
    assert data["size"] == test_file["size"]

async def test_list_documents(client, test_user_token):
    response = await client.get(
        f"{settings.api_v1_prefix}/documents/",
        headers={"Authorization": f"Bearer {test_user_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

async def test_get_document(client, test_user_token, test_file):
    # First upload a document
    file = BytesIO(test_file["content"])
    files = {"file": (test_file["filename"], file, test_file["content_type"])}
    upload_response = await client.post(
        f"{settings.api_v1_prefix}/documents/",
        files=files,
        headers={"Authorization": f"Bearer {test_user_token}"}
    )
    document_id = upload_response.json()["id"]
    
    # Then get its metadata
    response = await client.get(
        f"{settings.api_v1_prefix}/documents/{document_id}",
        headers={"Authorization": f"Bearer {test_user_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == document_id

async def test_download_document(client, test_user_token, test_file):
    # First upload a document
    file = BytesIO(test_file["content"])
    files = {"file": (test_file["filename"], file, test_file["content_type"])}
    upload_response = await client.post(
        f"{settings.api_v1_prefix}/documents/",
        files=files,
        headers={"Authorization": f"Bearer {test_user_token}"}
    )
    document_id = upload_response.json()["id"]
    
    # Then download it
    response = await client.get(
        f"{settings.api_v1_prefix}/documents/{document_id}/download",
        headers={"Authorization": f"Bearer {test_user_token}"}
    )
    
    assert response.status_code == 200
    assert response.content == test_file["content"]
    assert response.headers["content-type"] == test_file["content_type"]

async def test_delete_document(client, test_user_token, test_file):
    # First upload a document
    file = BytesIO(test_file["content"])
    files = {"file": (test_file["filename"], file, test_file["content_type"])}
    upload_response = await client.post(
        f"{settings.api_v1_prefix}/documents/",
        files=files,
        headers={"Authorization": f"Bearer {test_user_token}"}
    )
    document_id = upload_response.json()["id"]
    
    # Then delete it
    response = await client.delete(
        f"{settings.api_v1_prefix}/documents/{document_id}",
        headers={"Authorization": f"Bearer {test_user_token}"}
    )
    
    assert response.status_code == 200
    
    # Verify it's deleted
    get_response = await client.get(
        f"{settings.api_v1_prefix}/documents/{document_id}",
        headers={"Authorization": f"Bearer {test_user_token}"}
    )
    assert get_response.status_code == 404

async def test_unauthorized_access(client, test_file):
    response = await client.get(f"{settings.api_v1_prefix}/documents/")
    assert response.status_code == 401
    
    file = BytesIO(test_file["content"])
    files = {"file": (test_file["filename"], file, test_file["content_type"])}
    upload_response = await client.post(
        f"{settings.api_v1_prefix}/documents/",
        files=files
    )
    assert upload_response.status_code == 401
