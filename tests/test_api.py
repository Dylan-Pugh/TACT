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

@patch("tact.API.tact_api.controller.update_settings")
def test_config_patch_failure(mock_update_settings, client):
    mock_update_settings.return_value = False
    response = client.patch(
        "/config/parser",
        data=json.dumps({"new_key": "new_value"}),
        content_type="application/json"
    )
    assert response.status_code == 404

@patch("tact.API.tact_api.controller.update_settings")
def test_config_patch_no_data(mock_update_settings, client):
    response = client.patch(
        "/config/parser",
        data=json.dumps({}),
        content_type="application/json"
    )
    assert response.status_code == 400

@patch("tact.API.tact_api.controller.get_settings_json")
def test_config_get_field_success(mock_get_settings, client):
    mock_get_settings.return_value = {"field": "value", "other": "data"}
    response = client.get("/config/parser?field=field")
    assert response.status_code == 200
    assert response.json == "value"

@patch("tact.API.tact_api.controller.get_settings_json")
def test_config_get_field_not_found(mock_get_settings, client):
    mock_get_settings.return_value = {"field": "value"}
    response = client.get("/config/parser?field=missing")
    assert response.status_code == 404

# --- /upload ---
@patch("tact.API.tact_api.controller.update_settings")
@patch("tact.API.tact_api.controller.update_file_field_names")
def test_upload_lookup_type(mock_update_field_names, mock_update_settings, client):
    mock_update_settings.return_value = True
    data = {"file": (BytesIO(b"test data"), "lookup.csv")}
    response = client.post("/upload?type=lookup", data=data, content_type="multipart/form-data")
    assert response.status_code == 200
    mock_update_field_names.assert_called_once_with("lookup", "lookup_field_names")

@patch("tact.API.tact_api.controller.update_settings")
def test_upload_success(mock_update_settings, client):
    mock_update_settings.return_value = True
    data = {"file": (BytesIO(b"test data"), "test.csv")}
    response = client.post("/upload", data=data, content_type="multipart/form-data")
    assert response.status_code == 200
    assert b"uploaded" in response.data

@patch("tact.API.tact_api.controller.update_settings")
def test_upload_no_file(mock_update_settings, client):
    response = client.post("/upload", data={}, content_type="multipart/form-data")
    assert response.status_code == 400

@patch("tact.API.tact_api.controller.update_settings")
def test_upload_no_valid_files(mock_update_settings, client):
    # Send a file with empty filename
    data = {"file": (BytesIO(b"test"), "")}
    response = client.post("/upload", data=data, content_type="multipart/form-data")
    assert response.status_code == 400

@patch("tact.API.tact_api.controller.update_settings")
def test_upload_config_update_failure(mock_update_settings, client):
    mock_update_settings.return_value = False
    data = {"file": (BytesIO(b"test data"), "test.csv")}
    response = client.post("/upload", data=data, content_type="multipart/form-data")
    assert response.status_code == 500

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

@patch("tact.API.tact_api.controller.generate_preview")
def test_preview_failure(mock_generate_preview, client):
    mock_generate_preview.return_value = None
    response = client.get("/preview")
    assert response.status_code == 404

@patch("tact.API.tact_api.controller.generate_taxonomic_preview")
def test_preview_taxonomic_success(mock_generate_taxonomic, client):
    mock_generate_taxonomic.return_value = {"taxonomic": "data"}
    response = client.get("/preview?preview_type=taxonomic_names")
    assert response.status_code == 200

@patch("tact.API.tact_api.controller.generate_taxonomic_preview")
def test_preview_taxonomic_failure(mock_generate_taxonomic, client):
    mock_generate_taxonomic.return_value = None
    response = client.get("/preview?preview_type=taxonomic_names")
    assert response.status_code == 404

# --- /process ---
@patch("tact.API.tact_api.controller.process")
def test_process_success(mock_process, client):
    mock_process.return_value = True
    response = client.get("/process")
    assert response.status_code == 200

@patch("tact.API.tact_api.controller.process")
def test_process_failure(mock_process, client):
    mock_process.return_value = False
    response = client.get("/process")
    assert response.status_code == 404
    assert b"processing failed" in response.data

# --- /data ---
@patch("tact.API.tact_api.controller.get_data")
def test_data_success(mock_get_data, client):
    mock_get_data.return_value = {"some": "data"}
    response = client.get("/data")
    assert response.status_code == 200

@patch("tact.API.tact_api.controller.get_data")
def test_data_failure(mock_get_data, client):
    mock_get_data.return_value = None
    response = client.get("/data")
    assert response.status_code == 404

# --- /transform ---
@patch("tact.API.tact_api.controller.flip_dataset")
def test_transform_enumerate(mock_flip, client):
    mock_flip.return_value = True
    response = client.post("/transform?operation=enumerate_columns")
    assert response.status_code == 200

@patch("tact.API.tact_api.controller.flip_dataset")
def test_transform_enumerate_failure(mock_flip, client):
    mock_flip.return_value = False
    response = client.post("/transform?operation=enumerate_columns")
    assert response.status_code == 404

@patch("tact.API.tact_api.controller.pivot_dataset")
def test_transform_pivot(mock_pivot, client):
    mock_pivot.return_value = True
    response = client.post("/transform?operation=pivot_columns")
    assert response.status_code == 200

@patch("tact.API.tact_api.controller.pivot_dataset")
def test_transform_pivot_failure(mock_pivot, client):
    mock_pivot.return_value = False
    response = client.post("/transform?operation=pivot_columns")
    assert response.status_code == 404

@patch("tact.API.tact_api.controller.combine_rows")
def test_transform_combine_rows(mock_combine, client):
    mock_combine.return_value = True
    response = client.post("/transform?operation=combine_rows")
    assert response.status_code == 200

@patch("tact.API.tact_api.controller.combine_rows")
def test_transform_combine_rows_failure(mock_combine, client):
    mock_combine.return_value = False
    response = client.post("/transform?operation=combine_rows")
    assert response.status_code == 404

@patch("tact.API.tact_api.controller.validate_taxonomic_names")
def test_transform_merge_taxa(mock_merge, client):
    mock_merge.return_value = True
    response = client.post("/transform?operation=merge_taxa")
    assert response.status_code == 200

@patch("tact.API.tact_api.controller.validate_taxonomic_names")
def test_transform_merge_taxa_failure(mock_merge, client):
    mock_merge.return_value = False
    response = client.post("/transform?operation=merge_taxa")
    assert response.status_code == 404

@patch("tact.API.tact_api.controller.merge_lookup_data")
def test_transform_merge_lookup(mock_merge, client):
    mock_merge.return_value = True
    response = client.post("/transform?operation=merge_lookup")
    assert response.status_code == 200

@patch("tact.API.tact_api.controller.merge_lookup_data")
def test_transform_merge_lookup_failure(mock_merge, client):
    mock_merge.return_value = False
    response = client.post("/transform?operation=merge_lookup")
    assert response.status_code == 404

@patch("tact.API.tact_api.controller.merge_lookup_data")
def test_transform_invalid_operation(mock_merge, client):
    response = client.post("/transform?operation=invalid_op")
    assert response.status_code == 400
    assert b"Invalid operation" in response.data

# --- /forecast ---
@patch("tact.API.tact_api.controller.generate_forecast")
def test_forecast_generate_success(mock_forecast, client):
    mock_forecast.return_value = {"forecast": [1, 2, 3]}
    response = client.get("/forecast?operation=generate")
    assert response.status_code == 200
    assert b"Forecast generated" in response.data

@patch("tact.API.tact_api.controller.generate_forecast")
def test_forecast_generate_failure(mock_forecast, client):
    mock_forecast.return_value = None
    response = client.get("/forecast?operation=generate")
    assert response.status_code == 404

@patch("tact.API.tact_api.controller.evaluate_forecast")
def test_forecast_evaluate_success(mock_evaluate, client):
    mock_evaluate.return_value = {"metadata": {}, "data": "val"}
    response = client.get("/forecast?operation=evaluate")
    assert response.status_code == 200
    assert b"Forecast evaluated" in response.data

@patch("tact.API.tact_api.controller.evaluate_forecast")
def test_forecast_evaluate_failure(mock_evaluate, client):
    mock_evaluate.return_value = None
    response = client.get("/forecast?operation=evaluate")
    assert response.status_code == 404

@patch("tact.API.tact_api.controller.evaluate_forecast")
def test_forecast_invalid_operation(mock_evaluate, client):
    response = client.get("/forecast?operation=invalid_op")
    assert response.status_code == 400
    assert b"Invalid operation" in response.data
