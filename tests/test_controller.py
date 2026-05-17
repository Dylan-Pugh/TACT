import pytest
from unittest.mock import patch, mock_open, MagicMock
from pathlib import Path
import json

import tact.control.controller as controller
from tact.util import constants

# --- get_settings_json ---
@patch("builtins.open", new_callable=mock_open, read_data='{"key": "value"}')
@patch.dict(constants.CONFIG_FILE_PATHS, {"test_config": "/path/to/test.json"})
def test_get_settings_json_success(mock_file):
    """
    Test that get_settings_json successfully loads and returns JSON data
    when the config type exists and the file is found.
    """
    result = controller.get_settings_json("test_config")
    assert result == {"key": "value"}
    mock_file.assert_called_once_with("/path/to/test.json")

@patch("builtins.open", side_effect=FileNotFoundError)
@patch.dict(constants.CONFIG_FILE_PATHS, {"test_config": "/path/to/test.json"})
def test_get_settings_json_not_found(mock_file):
    result = controller.get_settings_json("test_config")
    assert result is None

# --- update_settings ---
@patch("json.dump")
@patch("builtins.open", new_callable=mock_open, read_data='{"old": "val"}')
@patch.dict(constants.CONFIG_FILE_PATHS, {"test_config": "/path/to/test.json"})
def test_update_settings_success(mock_file, mock_json_dump):
    result = controller.update_settings("test_config", {"new": "data"})
    assert result is True
    # The first call is "r", second is "w"
    assert mock_file.call_count == 2
    # Check that json.dump was called
    mock_json_dump.assert_called_once()
    args, kwargs = mock_json_dump.call_args
    assert args[0] == {"old": "val", "new": "data"}

@patch("builtins.open", side_effect=FileNotFoundError)
@patch.dict(constants.CONFIG_FILE_PATHS, {"test_config": "/path/to/test.json"})
def test_update_settings_not_found(mock_file):
    result = controller.update_settings("test_config", {"new": "data"})
    assert result is False

# --- analyze ---
@patch("tact.control.controller.analyzer.process_file")
@patch("builtins.open", new_callable=mock_open, read_data='{"isDirectory": false, "inputPath": "test.csv", "inputFileEncoding": "utf-8"}')
def test_analyze_success(mock_file, mock_process_file):
    mock_process_file.return_value = True
    result = controller.analyze()
    assert result == constants.PARSER_CONFIG_FILE_PATH
    mock_process_file.assert_called_once_with(input_path="test.csv", input_encoding="utf-8")

@patch("tact.control.controller.analyzer.process_file")
@patch("builtins.open", new_callable=mock_open, read_data='{"isDirectory": false, "inputPath": "test.csv", "inputFileEncoding": "utf-8"}')
def test_analyze_failure(mock_file, mock_process_file):
    mock_process_file.return_value = False
    result = controller.analyze()
    assert result is None

# --- is_directory ---
@patch("os.path.isdir")
def test_is_directory(mock_isdir):
    mock_isdir.return_value = True
    assert controller.is_directory("/some/path") is True
    mock_isdir.assert_called_once_with("/some/path")

@patch("os.path.isdir")
def test_is_directory_false(mock_isdir):
    mock_isdir.return_value = False
    assert controller.is_directory("/some/path") is False
    mock_isdir.assert_called_once_with("/some/path")