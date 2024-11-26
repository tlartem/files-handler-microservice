from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient
from src.models import File
from uuid import uuid4
from src.main import app

client = TestClient(app)


@patch("src.repositories.FileRepository.get_by_uid", new_callable=AsyncMock)
def test_get_file_success(mock_get_by_uid):
    test_uid = uuid4()
    mock_file_record = File(
        uid=str(test_uid),
        original_name="test_document.pdf",
        file_size=2048,
        file_extension=".pdf",
        file_format="application/pdf",
    )
    mock_get_by_uid.return_value = mock_file_record

    response = client.get(f"/files/{test_uid}")

    mock_get_by_uid.assert_called_once_with(str(test_uid))

    assert response.status_code == 200
    assert response.json() == {
        "uid": str(mock_file_record.uid),
        "original_name": mock_file_record.original_name,
        "file_size": mock_file_record.file_size,
        "file_extension": mock_file_record.file_extension,
        "file_format": mock_file_record.file_format,
    }


@patch("src.repositories.FileRepository.get_by_uid", new_callable=AsyncMock)
def test_get_file_not_found(mock_get_by_uid):
    test_uid = uuid4()
    mock_get_by_uid.return_value = None

    response = client.get(f"/files/{test_uid}")

    mock_get_by_uid.assert_called_once_with(str(test_uid))

    assert response.status_code == 404
    assert response.json() == {"detail": "File not found"}


@patch("src.api.file_routes.DownloadFileService")
def test_download_file_success(mock_download_service):
    mock_service_instance = mock_download_service.return_value
    mock_service_instance.get_and_set_file_record = AsyncMock(return_value=True)
    mock_service_instance.get_file_locally = AsyncMock(return_value=True)
    mock_service_instance.get_file_stream = AsyncMock(return_value=b"file content")

    test_uid = str(uuid4())
    response = client.get(f"files/download/{test_uid}")

    print(mock_service_instance.get_and_set_file_record.call_args_list)
    mock_service_instance.get_and_set_file_record.assert_called_once_with(test_uid)
    mock_service_instance.get_file_locally.assert_called_once()
    mock_service_instance.get_file_stream.assert_called_once()

    assert response.status_code == 200
    assert response.content == b'"file content"'
