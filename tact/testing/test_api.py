import pytest
from unittest.mock import patch, MagicMock
from io import BytesIO
import json
from tact.API.tact_api import app

@pytest.fixture
def client():
    """A test client for the app."""
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

# --- /config ---
@patch("tact.API.tact_api.controller.get_settings_json")
def test_config_get_success(mock_get_settings, client):
    mock_get_settings.return_value = {"key": "value"}
    response = client.get("/config/parser")
    assert response.status_code == 200
    assert response.json == {"key": "value"}

@patch("tact.API.tact_api.controller.get_settings_json")
def test_config_get_failure(mock_get_settings, client):
    mock_get_settings.return_value = None
    response = client.get("/config/parser")
    assert response.status_code == 404

@patch("tact.API.tact_api.controller.update_settings")
def test_config_patch_success(mock_update_settings, client):
    mock_update_settings.return_value = True
    response = client.patch(
        "/config/parser", 
        data=json.dumps({"new_key": "new_value"}),
        content_type="application/json"
    )
    assert response.status_code == 200

# --- /upload ---
@patch("tact.API.tact_api.controller.update_settings")
# Mock path.exists to avoid trying to check /tmp directories we care about,
# or we can just let it create the folder in /tmp since /tmp is safe
def test_upload_success(mock_update_settings, client):
    mock_update_settings.return_value = True
    
    # We send a dummy file payload
    data = {
        "file": (BytesIO(b"test data"), "test.csv")
    }
    
    response = client.post("/upload", data=data, content_type="multipart/form-data")
    assert response.status_code == 200
    assert b"uploaded" in response.data

@patch("tact.API.tact_api.controller.update_settings")
def test_upload_no_file(mock_update_settings, client):
    response = client.post("/upload", data={}, content_type="multipart/form-data")
    assert response.status_code == 400

# --- /analysis ---
@patch("tact.API.tact_api.controller.analyze")
def test_analysis_endpoint_success(mock_analyze, client):
    mock_analyze.return_value = True
    response = client.get("/analysis")
    assert response.status_code == 200
    assert b"Analysis complete." in response.data
    mock_analyze.assert_called_once()

@patch("tact.API.tact_api.controller.analyze")
def test_analysis_endpoint_failure(mock_analyze, client):
    mock_analyze.return_value = False
    response = client.get("/analysis")
    assert response.status_code == 404
    assert b"Analysis failed." in response.data
    mock_analyze.assert_called_once()

# --- /preview ---
@patch("tact.API.tact_api.controller.generate_preview")
def test_preview_success(mock_generate_preview, client):
    mock_generate_preview.return_value = {"preview": "data"}
    response = client.get("/preview")
    assert response.status_code == 200

@patch("tact.API.tact_api.controller.generate_taxonomic_preview")
def test_preview_taxonomic_success(mock_generate_taxonomic, client):
    mock_generate_taxonomic.return_value = {"taxonomic": "data"}
    response = client.get("/preview?preview_type=taxonomic_names")
    assert response.status_code == 200

# --- /process ---
@patch("tact.API.tact_api.controller.process")
def test_process_success(mock_process, client):
    mock_process.return_value = True
    response = client.get("/process")
    assert response.status_code == 200

# --- /data ---
@patch("tact.API.tact_api.controller.get_data")
def test_data_success(mock_get_data, client):
    mock_get_data.return_value = {"some": "data"}
    response = client.get("/data")
    assert response.status_code == 200

# --- /transform ---
@patch("tact.API.tact_api.controller.flip_dataset")
def test_transform_enumerate(mock_flip, client):
    mock_flip.return_value = True
    response = client.post("/transform?operation=enumerate_columns")
    assert response.status_code == 200

@patch("tact.API.tact_api.controller.pivot_dataset")
def test_transform_pivot(mock_pivot, client):
    mock_pivot.return_value = True
    response = client.post("/transform?operation=pivot_columns")
    assert response.status_code == 200

@patch("tact.API.tact_api.controller.combine_rows")
def test_transform_combine_rows(mock_combine, client):
    mock_combine.return_value = True
    response = client.post("/transform?operation=combine_rows")
    assert response.status_code == 200
