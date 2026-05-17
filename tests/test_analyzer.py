import pytest
from unittest.mock import patch, mock_open, MagicMock
from tact.processing import analyzer
import tact.util.constants as constants

# --- find_date_components ---
def test_find_date_components_success():
    """
    Test that find_date_components accurately identifies date fields
    from a list of header/field names.
    """
    field_names = ["ID", "Temperature", "Date_collected", "Location"]
    result = analyzer.find_date_components(field_names)
    assert result == {"date": "Date_collected"}

def test_find_date_components_split_fields():
    """Test when year, month, and day are in separate fields."""
    field_names = ["ID", "Year", "Month", "Day", "Time"]
    result = analyzer.find_date_components(field_names)
    assert result == {"year": "Year", "month": "Month", "day": "Day"}

def test_find_date_components_not_found():
    """Test response when no date components are found."""
    field_names = ["ID", "Temperature", "Location"]
    result = analyzer.find_date_components(field_names)
    assert result == {"year": "Not Found", "month": "Not Found", "day": "Not Found"}

# --- find_time_field ---
def test_find_time_field_success():
    """Test that time fields can be accurately identified."""
    field_names = ["ID", "Temperature", "Time_collected", "Location"]
    result = analyzer.find_time_field(field_names)
    assert result == {"time": "Time_collected"}

def test_find_time_field_split_fields():
    """Test when hours, minutes, and seconds are in separate fields."""
    field_names = ["ID", "Hour", "Minute", "Second", "Date"]
    result = analyzer.find_time_field(field_names)
    assert result == {"hour": "Hour", "minute": "Minute", "second": "Second"}

def test_find_time_field_not_found():
    """Test response when no time components are found."""
    field_names = ["ID", "Temperature", "Location"]
    result = analyzer.find_time_field(field_names)
    assert result == {"hour": "Not Found", "minute": "Not Found", "second": "Not Found"}


# --- process_file ---
@patch("csv.DictReader")
@patch("json.dump")
@patch("builtins.open", new_callable=mock_open, read_data='{"isDirectory": false, "inputPath": "test.csv"}')
def test_process_file_file_mode(mock_file, mock_json_dump, mock_csv_reader):
    """
    Test that a single CSV file can be processed, extracting headers
    and identifying datetime components, then updating the config file.
    """
    # Setup mock CSV reader behavior
    mock_csv_reader_instance = MagicMock()
    mock_csv_reader_instance.fieldnames = ["Date", "Time", "Value"]
    mock_csv_reader.return_value = mock_csv_reader_instance
    
    result = analyzer.process_file("test.csv", "utf-8")
    
    assert result is True
    # The config should have been updated and written back
    mock_json_dump.assert_called_once()
    args, kwargs = mock_json_dump.call_args
    assert "fieldNames" in args[0]
    assert args[0]["fieldNames"] == ["Date", "Time", "Value"]
    assert "dateFields" in args[0]
    assert "timeField" in args[0]


@patch("os.listdir")
@patch("csv.DictReader")
@patch("json.dump")
@patch("builtins.open", new_callable=mock_open, read_data='{"isDirectory": true, "inputPath": "/tmp/testdir"}')
def test_process_file_directory_mode(mock_file, mock_json_dump, mock_csv_reader, mock_listdir):
    """
    Test that processing a directory successfully targets
    the first data file in that directory.
    """
    mock_listdir.return_value = ["file1.csv", "file2.csv", ".hidden"]
    
    mock_csv_reader_instance = MagicMock()
    mock_csv_reader_instance.fieldnames = ["Date", "Time", "Value"]
    mock_csv_reader.return_value = mock_csv_reader_instance
    
    result = analyzer.process_file("/tmp/testdir", "utf-8")
    
    assert result is True
    assert mock_listdir.called
    
    # Check if the pathForPreview was assigned to the first CSV
    mock_json_dump.assert_called_once()
    args, kwargs = mock_json_dump.call_args
    assert args[0]["pathForPreview"] == "/tmp/testdir/file1.csv"


# --- create_preview ---
@patch("tact.processing.datetime_parser.create_iso_time")
@patch("csv.DictReader")
@patch("builtins.open", new_callable=mock_open)
def test_create_preview(mock_file, mock_csv_reader, mock_create_iso_time):
    """
    Test that preview samples are generated accurately taking the top values.
    """
    # Setup mock config
    config = {
        "pathForPreview": "test.csv",
        "inputFileEncoding": "utf-8",
        "dateFields": {"date": "Date"},
        "timeField": {"time": "Time"}
    }
    
    # Setup mock CSV reader iteration -> returns an iterator so next() works
    # create_preview skips the first row via next(reader)
    mock_reader_instance = iter([
        {"Date": "2023-01-01", "Time": "12:00:00", "Value": "1"}, # This one gets next()ed away
        {"Date": "2023-01-02", "Time": "13:00:00", "Value": "2"}  # This one gets processed
    ])
    mock_csv_reader.return_value = mock_reader_instance
    
    mock_create_iso_time.return_value = "2023-01-02T13:00:00Z"
    
    result = analyzer.create_preview(config)
    
    assert "samples" in result
    assert len(result["samples"]) == 1
    sample = result["samples"][0]
    
    assert sample["Original_Date"] == "2023-01-02"
    assert sample["Transformation"] == "2023-01-02T13:00:00Z"
