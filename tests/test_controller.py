import pytest
from unittest.mock import patch, mock_open, MagicMock
from pathlib import Path
import json
import pandas as pd

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
    assert mock_file.call_count == 2
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


# --- generate_preview ---
@patch("tact.control.controller.analyzer.create_preview")
@patch("builtins.open", new_callable=mock_open, read_data='{"pathForPreview": "test.csv", "inputFileEncoding": "utf-8"}')
def test_generate_preview_success(mock_file, mock_create_preview):
    mock_create_preview.return_value = {"samples": [{"col": "val"}]}
    result = controller.generate_preview()
    assert result == {"samples": [{"col": "val"}]}
    mock_create_preview.assert_called_once()

@patch("tact.control.controller.analyzer.create_preview")
@patch("builtins.open", new_callable=mock_open, read_data='{"pathForPreview": "test.csv", "inputFileEncoding": "utf-8"}')
def test_generate_preview_returns_none(mock_file, mock_create_preview):
    mock_create_preview.return_value = None
    result = controller.generate_preview()
    assert result is None


# --- get_data ---
@patch("tact.control.controller.Path")
@patch("pandas.read_csv")
@patch("builtins.open", new_callable=mock_open, read_data='{"inputPath": "test.csv"}')
def test_get_data_default_format(mock_file, mock_read_csv, mock_path_cls):
    """Test get_data returns dict by default."""
    mock_df = MagicMock(spec=pd.DataFrame)
    mock_df.to_dict.return_value = {"a": [1, 2]}
    mock_read_csv.return_value = mock_df
    mock_path = MagicMock()
    mock_path.return_value = mock_path
    mock_path.suffix = ".csv"
    mock_path.is_dir.return_value = False
    mock_path_cls.return_value = mock_path

    result = controller.get_data()
    assert result == {"a": [1, 2]}
    mock_df.to_dict.assert_called_once()

@patch("tact.control.controller.Path")
@patch("pandas.read_csv")
@patch("builtins.open", new_callable=mock_open, read_data='{"inputPath": "test.csv"}')
def test_get_data_dataframe_format(mock_file, mock_read_csv, mock_path_cls):
    """Test get_data returns DataFrame when format='dataframe'."""
    mock_df = MagicMock(spec=pd.DataFrame)
    mock_read_csv.return_value = mock_df
    mock_path = MagicMock()
    mock_path.return_value = mock_path
    mock_path.suffix = ".csv"
    mock_path.is_dir.return_value = False
    mock_path_cls.return_value = mock_path

    result = controller.get_data(kwargs={"format": "dataframe"})
    assert result is mock_df
    mock_df.to_dict.assert_not_called()

@patch("tact.control.controller.Path")
@patch("pandas.read_csv")
@patch("builtins.open", new_callable=mock_open, read_data='{"inputPath": "test.csv"}')
def test_get_data_json_format(mock_file, mock_read_csv, mock_path_cls):
    """Test get_data returns JSON string when format='json'."""
    mock_df = MagicMock(spec=pd.DataFrame)
    mock_df.to_json.return_value = '{"a":[1,2]}'
    mock_read_csv.return_value = mock_df
    mock_path = MagicMock()
    mock_path.return_value = mock_path
    mock_path.suffix = ".csv"
    mock_path.is_dir.return_value = False
    mock_path_cls.return_value = mock_path

    result = controller.get_data(kwargs={"format": "json"})
    assert result == '{"a":[1,2]}'
    mock_df.to_json.assert_called_once()

@patch("tact.control.controller.Path")
@patch("pandas.read_csv")
@patch("builtins.open", new_callable=mock_open, read_data='{"transform_output_path": "output.csv"}')
def test_get_data_transform_request_type(mock_file, mock_read_csv, mock_path_cls):
    """Test get_data with request_type='transform' reads transform_output_path."""
    mock_df = MagicMock(spec=pd.DataFrame)
    mock_df.to_dict.return_value = {"data": "val"}
    mock_read_csv.return_value = mock_df
    mock_path = MagicMock()
    mock_path.return_value = mock_path
    mock_path.suffix = ".csv"
    mock_path.is_dir.return_value = False
    mock_path_cls.return_value = mock_path

    result = controller.get_data(kwargs={"request_type": "transform"})
    assert result == {"data": "val"}

@patch("tact.control.controller.Path")
@patch("pandas.read_csv")
@patch("builtins.open", new_callable=mock_open, read_data='{"lookup_path": "lookup.csv"}')
def test_get_data_lookup_request_type(mock_file, mock_read_csv, mock_path_cls):
    """Test get_data with request_type='lookup' reads lookup_file_path."""
    mock_df = MagicMock(spec=pd.DataFrame)
    mock_df.to_dict.return_value = {"lookup": "data"}
    mock_read_csv.return_value = mock_df
    mock_path = MagicMock()
    mock_path.return_value = mock_path
    mock_path.suffix = ".csv"
    mock_path.is_dir.return_value = False
    mock_path_cls.return_value = mock_path

    result = controller.get_data(kwargs={"request_type": "lookup"})
    assert result == {"lookup": "data"}

@patch("tact.control.controller.Path")
@patch("pandas.read_csv")
@patch("builtins.open", new_callable=mock_open, read_data='{"inputPath": "test.csv"}')
def test_get_data_file_not_found(mock_file, mock_read_csv, mock_path_cls):
    """Test get_data returns None when file is not found."""
    mock_read_csv.side_effect = FileNotFoundError("file not found")
    mock_path = MagicMock()
    mock_path.return_value = mock_path
    mock_path.suffix = ".csv"
    mock_path.is_dir.return_value = False
    mock_path_cls.return_value = mock_path

    result = controller.get_data()
    assert result is None

@patch("tact.control.controller.Path")
@patch("pandas.read_csv")
@patch("builtins.open", new_callable=mock_open, read_data='{"inputPath": "test.csv"}')
def test_get_data_invalid_format_conversion(mock_file, mock_read_csv, mock_path_cls):
    """Test get_data returns None when conversion to format fails."""
    mock_df = MagicMock(spec=pd.DataFrame)
    mock_df.to_dict.side_effect = ValueError("conversion failed")
    mock_read_csv.return_value = mock_df
    mock_path = MagicMock()
    mock_path.return_value = mock_path
    mock_path.suffix = ".csv"
    mock_path.is_dir.return_value = False
    mock_path_cls.return_value = mock_path

    result = controller.get_data()
    assert result is None

@patch("tact.control.controller.Path")
@patch("pandas.read_csv")
@patch("builtins.open", new_callable=mock_open, read_data='{"transform_output_path": "output.csv"}')
def test_get_data_nc_file_raises(mock_file, mock_read_csv, mock_path_cls):
    """Test that .nc files raise NotImplementedError."""
    mock_path = MagicMock()
    mock_path.return_value = mock_path
    mock_path.suffix = ".nc"
    mock_path.is_dir.return_value = False
    mock_path_cls.return_value = mock_path

    with pytest.raises(NotImplementedError):
        controller.get_data(kwargs={"request_type": "transform"})

@patch("tact.control.controller.Path")
@patch("tact.control.controller.update_settings")
@patch("pandas.read_csv")
@patch("builtins.open", new_callable=mock_open, read_data='{"inputPath": "/tmp/testdir"}')
def test_get_data_directory_input_updates_parser_config(mock_file, mock_read_csv, mock_update, mock_path_cls):
    """Test that directory input triggers update_settings for parser config."""
    mock_df = MagicMock(spec=pd.DataFrame)
    mock_df.to_dict.return_value = {"data": "val"}
    mock_read_csv.return_value = mock_df
    mock_path = MagicMock()
    mock_path.return_value = mock_path
    mock_path.suffix = ".csv"
    mock_path.is_dir.return_value = True
    mock_file_path = MagicMock()
    mock_file_path.is_file.return_value = True
    mock_file_path.name = "test.csv"
    mock_file_path.suffix = ".csv"
    mock_path.iterdir.return_value = [mock_file_path]
    mock_path_cls.return_value = mock_path

    result = controller.get_data()
    assert result == {"data": "val"}
    mock_update.assert_called()

@patch("tact.control.controller.Path")
@patch("tact.control.controller.update_settings")
@patch("pandas.read_csv")
@patch("builtins.open", new_callable=mock_open, read_data='{"lookup_path": "/tmp/testdir"}')
def test_get_data_lookup_type_skips_directory_update(mock_file, mock_read_csv, mock_update, mock_path_cls):
    """Test that request_type='lookup' skips directory update_settings."""
    # This test verifies the guard: if request_type == "lookup", update_settings should not be called
    # even when the path is a directory
    mock_df = MagicMock(spec=pd.DataFrame)
    mock_df.to_dict.return_value = {"lookup": "data"}
    mock_read_csv.return_value = mock_df
    mock_path = MagicMock()
    mock_path.return_value = mock_path
    mock_path.suffix = ".csv"
    mock_path.is_dir.return_value = True
    mock_path_cls.return_value = mock_path

    result = controller.get_data(kwargs={"request_type": "lookup"})
    assert result == {"lookup": "data"}
    # update_settings should NOT be called for lookup type
    mock_update.assert_not_called()

@patch("tact.control.controller.Path")
@patch("pandas.read_csv")
@patch("builtins.open", new_callable=mock_open, read_data='{"inputPath": "test.csv"}')
def test_get_data_nrows_parsing(mock_file, mock_read_csv, mock_path_cls):
    """Test that nrows kwarg is parsed as int."""
    mock_df = MagicMock(spec=pd.DataFrame)
    mock_df.to_dict.return_value = {"data": "val"}
    mock_read_csv.return_value = mock_df
    mock_path = MagicMock()
    mock_path.return_value = mock_path
    mock_path.suffix = ".csv"
    mock_path.is_dir.return_value = False
    mock_path_cls.return_value = mock_path

    controller.get_data(kwargs={"nrows": "10"})
    mock_read_csv.assert_called_once()
    call_kwargs = mock_read_csv.call_args[1]
    assert call_kwargs["nrows"] == 10

@patch("tact.control.controller.Path")
@patch("pandas.read_csv")
@patch("builtins.open", new_callable=mock_open, read_data='{"inputPath": "test.csv"}')
def test_get_data_invalid_nrows_logs_error(mock_file, mock_read_csv, mock_path_cls, caplog):
    """Test that invalid nrows value is logged but doesn't crash."""
    mock_df = MagicMock(spec=pd.DataFrame)
    mock_df.to_dict.return_value = {"data": "val"}
    mock_read_csv.return_value = mock_df
    mock_path = MagicMock()
    mock_path.return_value = mock_path
    mock_path.suffix = ".csv"
    mock_path.is_dir.return_value = False
    mock_path_cls.return_value = mock_path

    result = controller.get_data(kwargs={"nrows": "not_a_number"})
    assert result == {"data": "val"}
    assert "Error parsing nrows arg" in caplog.text


# --- process ---
@patch("tact.control.controller.update_settings")
@patch("tact.util.csv_utils.write_out_data_frame")
@patch("tact.util.csv_utils.drop_duplicate_columns")
@patch("tact.util.csv_utils.drop_unnamed_columns")
@patch("tact.util.csv_utils.delete_columns")
@patch("tact.util.csv_utils.replace_char_in_headers")
@patch("tact.util.csv_utils.append_row_header")
@patch("tact.util.csv_utils.replace_in_rows")
@patch("tact.util.csv_utils.concat_input_files")
@patch("tact.processing.datetime_parser.compile_datetime")
@patch("pandas.read_csv")
@patch("builtins.open", new_callable=mock_open, read_data='{"isDirectory": false, "inputPath": "test.csv", "inputFileEncoding": "utf-8", "fixTimes": false, "dropDuplicates": false, "dropEmpty": false, "normalizeHeaders": false, "appendHeaders": false, "replaceValues": false, "deleteColumns": false, "concatFiles": false, "outputFilePath": "out.csv", "fieldNames": ["A", "B"], "columnsToDelete": ["A"]}')
def test_process_single_file(mock_file, mock_read_csv, mock_compile, mock_concat,
                              mock_replace, mock_append, mock_replace_headers,
                              mock_delete, mock_drop_empty, mock_drop_dup,
                              mock_write, mock_update):
    """Test processing a single file with no additional fixes."""
    mock_read_csv.return_value = pd.DataFrame({"A": [1], "B": [2]})
    mock_compile.return_value = "output"
    result = controller.process()
    assert result is True


@patch("tact.control.controller.update_settings")
@patch("tact.util.csv_utils.write_out_data_frame")
@patch("tact.util.csv_utils.drop_duplicate_columns")
@patch("tact.util.csv_utils.drop_unnamed_columns")
@patch("tact.util.csv_utils.delete_columns")
@patch("tact.util.csv_utils.replace_char_in_headers")
@patch("tact.util.csv_utils.append_row_header")
@patch("tact.util.csv_utils.replace_in_rows")
@patch("tact.util.csv_utils.concat_input_files")
@patch("tact.processing.datetime_parser.compile_datetime")
@patch("pandas.read_csv")
@patch("builtins.open", new_callable=mock_open, read_data='{"isDirectory": true, "inputPath": "/tmp/testdir", "targetFiles": ["/tmp/testdir/file.csv"], "inputFileEncoding": "utf-8", "fixTimes": true, "dropDuplicates": true, "dropEmpty": true, "normalizeHeaders": true, "appendHeaders": true, "replaceValues": true, "deleteColumns": true, "concatFiles": true, "outputFilePath": "out.csv", "fieldNames": ["A", "B"], "columnsToDelete": ["A"], "dateFields": {"date": "Date"}, "timeField": {"time": "Time"}, "parsedColumnName": "parsed_time", "parsedColumnPosition": 0, "headerValuesToReplace": [{"original": " ", "replacement": "_"}], "rowValuesToReplace": [{"original": "old", "replacement": "new"}], "rowForColumnAppend": 0, "dropAppendedRow": false}')
def test_process_directory_concat(mock_file, mock_read_csv, mock_compile, mock_concat,
                                   mock_replace, mock_append, mock_replace_headers,
                                   mock_delete, mock_drop_empty, mock_drop_dup,
                                   mock_write, mock_update):
    """Test processing a directory with concatFiles enabled."""
    mock_read_csv.return_value = pd.DataFrame({"A": [1], "B": [2]})
    mock_compile.return_value = "output"
    result = controller.process()
    assert result is True
    mock_concat.assert_called()


# --- flip_dataset ---
@patch("tact.control.controller.update_settings")
@patch("tact.util.csv_utils.write_out_data_frame")
@patch("tact.processing.dataset_flipper.process")
@patch("tact.control.controller.get_data")
@patch("tact.control.controller.get_settings_json")
def test_flip_dataset_success(mock_get_settings, mock_get_data, mock_flipper, mock_write, mock_update):
    """Test successful dataset flip."""
    mock_get_settings.side_effect = [
        {"transform_output_path": "out.csv", "target_data_columns": ["col1"], "drop_units": False, "drop_empty_records": False, "split_fields": False, "delimiter": ",", "split_column_name": "split", "match_col_variants": False, "primary_units": None, "alt_units": None, "set_occurrence_status": False, "gen_UUID": False, "results_column": "results", "constants": {}},
        {"inputFileEncoding": "utf-8"},
    ]
    mock_get_data.return_value = pd.DataFrame({"col1": [1, 2]})
    mock_flipper.return_value = pd.DataFrame({"results": ["a", "b"]})
    result = controller.flip_dataset()
    assert result is True
    mock_write.assert_called_once()


# --- pivot_dataset ---
@patch("tact.control.controller.update_settings")
@patch("tact.util.csv_utils.write_out_data_frame")
@patch("tact.processing.dataset_flipper.pivot")
@patch("tact.control.controller.get_data")
@patch("tact.control.controller.get_settings_json")
def test_pivot_dataset_success(mock_get_settings, mock_get_data, mock_pivot, mock_write, mock_update):
    """Test successful dataset pivot."""
    mock_get_settings.side_effect = [
        {"transform_output_path": "out.csv", "pivot_column": "col1", "pivot_value_column": "col2"},
        {"inputFileEncoding": "utf-8"},
    ]
    mock_get_data.return_value = pd.DataFrame({"col1": ["a", "b"], "col2": [1, 2]})
    mock_pivot.return_value = pd.DataFrame({"a": [1], "b": [2]})
    result = controller.pivot_dataset()
    assert result is True
    mock_write.assert_called_once()


# --- combine_rows ---
@patch("tact.control.controller.update_settings")
@patch("tact.util.csv_utils.write_out_data_frame")
@patch("tact.util.csv_utils.combine_rows")
@patch("tact.control.controller.get_data")
@patch("tact.control.controller.get_settings_json")
def test_combine_rows_success(mock_get_settings, mock_get_data, mock_combine, mock_write, mock_update):
    """Test successful row combination."""
    mock_get_settings.side_effect = [
        {"transform_output_path": "out.csv", "combine_output_path": "combined.csv", "match_columns": ["key"], "append_prefix": "ADDED_", "match_pattern": None},
        {"inputFileEncoding": "utf-8"},
    ]
    mock_get_data.return_value = pd.DataFrame({"key": ["A", "A"], "val": [1, 2]})
    mock_combine.return_value = pd.DataFrame({"key": ["A"], "val": [1]})
    result = controller.combine_rows()
    assert result is None  # combine_rows returns None
    mock_write.assert_called_once()


# --- validate_taxonomic_names ---
@patch("tact.control.controller.update_settings")
@patch("tact.util.csv_utils.write_out_data_frame")
@patch("pandas.read_csv")
@patch("tact.processing.taxonomic_name_matcher.merge_matched_taxa")
@patch("tact.control.controller.get_data")
@patch("tact.control.controller.get_settings_json")
def test_validate_taxonomic_names_success(mock_get_settings, mock_get_data, mock_merge, mock_read_csv, mock_write, mock_update):
    """Test successful taxonomic name validation."""
    mock_get_settings.side_effect = [
        {"transform_output_path": "out.csv", "target_column_for_taxon": "scientificName", "accepted_taxon_matches": ["Species A"]},
        {"inputFileEncoding": "utf-8"},
    ]
    mock_get_data.return_value = pd.DataFrame({"scientificName": ["Species A", "Species B"]})
    mock_read_csv.return_value = pd.DataFrame({"scientificName": ["Species A"], "acceptedname": ["Species A accepted"]})
    mock_merge.return_value = pd.DataFrame({"scientificName": ["Species A", "Species B"], "acceptedname": ["Species A accepted", ""]})
    result = controller.validate_taxonomic_names()
    assert result is True

@patch("tact.control.controller.update_settings")
@patch("tact.util.csv_utils.write_out_data_frame")
@patch("pandas.read_csv")
@patch("tact.processing.taxonomic_name_matcher.merge_matched_taxa")
@patch("tact.control.controller.get_data")
@patch("tact.control.controller.get_settings_json")
def test_validate_taxonomic_names_failure(mock_get_settings, mock_get_data, mock_merge, mock_read_csv, mock_write, mock_update, caplog):
    """Test taxonomic name validation failure."""
    mock_get_settings.side_effect = [
        {"transform_output_path": "out.csv", "target_column_for_taxon": "scientificName", "accepted_taxon_matches": ["Species A"]},
        {"inputFileEncoding": "utf-8"},
    ]
    mock_get_data.return_value = pd.DataFrame({"scientificName": ["Species A"]})
    mock_read_csv.side_effect = Exception("WORMS lookup missing")
    result = controller.validate_taxonomic_names()
    assert result is False


# --- merge_lookup_data ---
@patch("tact.control.controller.update_settings")
@patch("tact.util.csv_utils.write_out_data_frame")
@patch("tact.processing.lookup_merger.merge_matched_records")
@patch("tact.control.controller.get_data")
@patch("tact.control.controller.get_settings_json")
def test_merge_lookup_data_success(mock_get_settings, mock_get_data, mock_merge, mock_write, mock_update):
    """Test successful lookup merge."""
    mock_get_settings.side_effect = [
        {"transform_output_path": "out.csv", "lookup_file_path": "lookup.csv", "lookup_key_column": "id", "target_key_column": "station_id", "lookup_value_columns": ["region"], "lookup_output_path": "merged.csv"},
        {"inputFileEncoding": "utf-8"},
    ]
    mock_get_data.side_effect = [
        pd.DataFrame({"station_id": ["A1", "B2"], "temp": [20, 22]}),
        pd.DataFrame({"id": ["A1"], "region": ["North"]}),
    ]
    mock_merge.return_value = pd.DataFrame({"station_id": ["A1", "B2"], "temp": [20, 22], "region": ["North", None]})
    result = controller.merge_lookup_data()
    assert result is True
    mock_write.assert_called_once()

@patch("tact.control.controller.update_settings")
@patch("tact.util.csv_utils.write_out_data_frame")
@patch("tact.processing.lookup_merger.merge_matched_records")
@patch("tact.control.controller.get_data")
@patch("tact.control.controller.get_settings_json")
def test_merge_lookup_data_lookup_read_failure(mock_get_settings, mock_get_data, mock_merge, mock_write, mock_update, caplog):
    """Test lookup merge when lookup file can't be read."""
    mock_get_settings.side_effect = [
        {"transform_output_path": "out.csv", "lookup_file_path": "lookup.csv", "lookup_key_column": "id", "target_key_column": "station_id", "lookup_value_columns": ["region"], "lookup_output_path": "merged.csv"},
        {"inputFileEncoding": "utf-8"},
    ]
    mock_get_data.side_effect = [
        pd.DataFrame({"station_id": ["A1"]}),
        Exception("File not found"),
    ]
    result = controller.merge_lookup_data()
    assert result is False
    assert "Failed to read lookup file" in caplog.text

@patch("tact.control.controller.update_settings")
@patch("tact.util.csv_utils.write_out_data_frame")
@patch("tact.processing.lookup_merger.merge_matched_records")
@patch("tact.control.controller.get_data")
@patch("tact.control.controller.get_settings_json")
def test_merge_lookup_data_returns_none(mock_get_settings, mock_get_data, mock_merge, mock_write, mock_update, caplog):
    """Test lookup merge when merge function returns None."""
    mock_get_settings.side_effect = [
        {"transform_output_path": "out.csv", "lookup_file_path": "lookup.csv", "lookup_key_column": "id", "target_key_column": "station_id", "lookup_value_columns": ["region"], "lookup_output_path": "merged.csv"},
        {"inputFileEncoding": "utf-8"},
    ]
    mock_get_data.side_effect = [
        pd.DataFrame({"station_id": ["A1"]}),
        pd.DataFrame({"id": ["A1"], "region": ["North"]}),
    ]
    mock_merge.return_value = None
    result = controller.merge_lookup_data()
    assert result is False
    assert "Merge returned None" in caplog.text


# --- update_file_field_names ---
@patch("tact.control.controller.update_settings")
@patch("tact.control.controller.get_data")
def test_update_file_field_names_success(mock_get_data, mock_update):
    """update_file_field_names reads columns via get_data and writes them to config."""
    mock_get_data.return_value = pd.DataFrame({"col_a": [1], "col_b": [2], "col_c": [3]})
    controller.update_file_field_names("lookup", "lookup_field_names")
    mock_get_data.assert_called_once_with(kwargs={"format": "dataframe", "nrows": 0, "request_type": "lookup"})
    mock_update.assert_called_once_with("lookup", {"lookup_field_names": ["col_a", "col_b", "col_c"]})

@patch("tact.control.controller.update_settings")
@patch("tact.control.controller.get_data")
def test_update_file_field_names_failure(mock_get_data, mock_update, caplog):
    """Failed CSV read is logged and an empty list is stored, without crashing."""
    mock_get_data.side_effect = Exception("File not found")
    controller.update_file_field_names("lookup", "lookup_field_names")
    mock_update.assert_called_once_with("lookup", {"lookup_field_names": []})
    assert "Failed to read column names" in caplog.text

def test_lookup_upload_key_alignment():
    """CONFIG_FILE_PATH_KEYS["lookup"] must match the key written by the upload handler.

    The upload handler stores the file path under "lookup_path" in transformConfig.JSON.
    get_data(request_type="lookup") resolves the file path via CONFIG_FILE_PATH_KEYS["lookup"].
    If these diverge, field-name caching silently reads a stale path instead of the
    uploaded file — the regression introduced when "lookup_file_path" was used instead.
    """
    upload_write_key = "lookup_path"
    assert constants.CONFIG_FILE_PATH_KEYS["lookup"] == upload_write_key, (
        f"CONFIG_FILE_PATH_KEYS['lookup'] is '{constants.CONFIG_FILE_PATH_KEYS['lookup']}' "
        f"but the upload handler writes to '{upload_write_key}'. "
        "These must match or update_file_field_names will read a stale path."
    )

def test_comparison_upload_key_alignment():
    """CONFIG_FILE_PATH_KEYS["comparison"] must match the key written by the upload handler."""
    upload_write_key = "dataset2_path"
    assert constants.CONFIG_FILE_PATH_KEYS["comparison"] == upload_write_key, (
        f"CONFIG_FILE_PATH_KEYS['comparison'] is '{constants.CONFIG_FILE_PATH_KEYS['comparison']}' "
        f"but the upload handler writes to '{upload_write_key}'."
    )


# --- generate_forecast ---
@patch("tact.control.controller.get_settings_json")
@patch("tact.control.controller.get_data")
@patch("tact.processing.forecaster.forecast_csv")
def test_generate_forecast_success(mock_forecast, mock_get_data, mock_get_settings):
    """Test successful forecast generation."""
    mock_get_settings.return_value = {"horizon": 10, "date_column": "date", "target_data_columns": ["temp"]}
    mock_get_data.return_value = pd.DataFrame({"date": ["2023-01-01", "2023-01-02"], "temp": [20, 22]})
    mock_forecast.return_value = pd.DataFrame({"series": ["temp"], "step": [1], "forecast": [21.0]})
    result = controller.generate_forecast()
    assert result == {"series": ["temp"], "step": [1], "forecast": [21.0]}
    mock_forecast.assert_called_once()


# --- evaluate_forecast ---
@patch("tact.control.controller.get_settings_json")
@patch("tact.control.controller.get_data")
@patch("tact.processing.forecaster.evaluate_forecast")
def test_evaluate_forecast_success(mock_evaluate, mock_get_data, mock_get_settings):
    """Test successful forecast evaluation."""
    mock_get_settings.return_value = {"date_column": "date", "target_data_columns": ["temp"]}
    mock_get_data.return_value = pd.DataFrame({"date": ["2023-01-01", "2023-01-02", "2023-01-03"], "temp": [20, 22, 21]})
    mock_evaluate.return_value = ({"score": 85}, pd.DataFrame({"date": ["2023-01-03"], "temp": [21], "temp_forecast": [21.5]}))
    result = controller.evaluate_forecast()
    assert "metadata" in result
    assert "date" in result
    assert "temp" in result
    mock_evaluate.assert_called_once()
