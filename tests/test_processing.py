"""
Tests for processing modules: dataset_flipper, datetime_parser, quality_checker, xml_generator.
"""

import logging
import os
import csv
import datetime
import pytest
import pandas as pd
from unittest.mock import patch, MagicMock, mock_open


# -----------------------------------------------------------------------------
# dataset_flipper
# -----------------------------------------------------------------------------

from tact.processing import dataset_flipper


@pytest.fixture
def sample_row_dict():
    return pd.Series({"station": "A1", "species_count": 10, "temp": 22.5})


@pytest.fixture
def sample_row():
    return ("0", sample_row_dict())


@pytest.fixture
def mock_constants():
    return {"country": "US", "project": "TACT"}


@pytest.fixture
def mock_constants_empty():
    return {}


@pytest.fixture
def sample_df():
    return pd.DataFrame({
        "date": ["2023-01-01", "2023-01-02"],
        "species_A": [10, 5],
        "species_B": [3, 0],
    })


# -- enumerate_row --

def test_enumerate_row_sets_results_column(split_fields=True):
    row = ("0", pd.Series({"species_A": 10, "temp": 22.5}))
    result = dataset_flipper.enumerate_row(
        row=row,
        field="species_A",
        results_column="species",
        split_fields=True,
        delimiter="_",
        split_column_name="life_stage",
        match_col_variants=False,
        primary_units="organismQuantity",
        alt_units=None,
        set_occurrence_status=True,
        gen_UUID=True,
        constants={},
    )
    assert result["species"] == "species"


def test_enumerate_row_sets_split_column_when_multiple_parts():
    row = ("0", pd.Series({"life_stage_A": 10, "temp": 22.5}))
    result = dataset_flipper.enumerate_row(
        row=row,
        field="life_stage_A",
        results_column="species",
        split_fields=True,
        delimiter="_",
        split_column_name="life_stage",
        match_col_variants=False,
        primary_units=None,
        alt_units=None,
        set_occurrence_status=False,
        gen_UUID=False,
        constants={},
    )
    assert result["life_stage"] == "stage"


def test_enumerate_row_sets_split_column_to_none_when_single_part():
    row = ("0", pd.Series({"species": 10, "temp": 22.5}))
    result = dataset_flipper.enumerate_row(
        row=row,
        field="species",
        results_column="species",
        split_fields=True,
        delimiter="_",
        split_column_name="life_stage",
        match_col_variants=False,
        primary_units=None,
        alt_units=None,
        set_occurrence_status=False,
        gen_UUID=False,
        constants={},
    )
    assert result["life_stage"] is None


def test_enumerate_row_sets_primary_units_when_provided():
    row = ("0", pd.Series({"species_A": 10, "temp": 22.5}))
    result = dataset_flipper.enumerate_row(
        row=row,
        field="species_A",
        results_column="species",
        split_fields=False,
        delimiter="_",
        split_column_name="life_stage",
        match_col_variants=False,
        primary_units="count",
        alt_units=None,
        set_occurrence_status=False,
        gen_UUID=False,
        constants={},
    )
    assert result["count"] == 10


def test_enumerate_row_sets_default_organism_quantity_when_no_primary_units():
    row = ("0", pd.Series({"species_A": 10, "temp": 22.5}))
    result = dataset_flipper.enumerate_row(
        row=row,
        field="species_A",
        results_column="species",
        split_fields=False,
        delimiter="_",
        split_column_name="life_stage",
        match_col_variants=False,
        primary_units=None,
        alt_units=None,
        set_occurrence_status=False,
        gen_UUID=False,
        constants={},
    )
    assert result["organismQuantity"] == 10


def test_enumerate_row_sets_occurrence_status_present_when_positive():
    row = ("0", pd.Series({"species_A": 10, "temp": 22.5}))
    result = dataset_flipper.enumerate_row(
        row=row,
        field="species_A",
        results_column="species",
        split_fields=False,
        delimiter="_",
        split_column_name="life_stage",
        match_col_variants=False,
        primary_units=None,
        alt_units=None,
        set_occurrence_status=True,
        gen_UUID=False,
        constants={},
    )
    assert result["occurrenceStatus"] == "present"


def test_enumerate_row_sets_occurrence_status_absent_when_zero():
    row = ("0", pd.Series({"species_A": 0, "temp": 22.5}))
    result = dataset_flipper.enumerate_row(
        row=row,
        field="species_A",
        results_column="species",
        split_fields=False,
        delimiter="_",
        split_column_name="life_stage",
        match_col_variants=False,
        primary_units=None,
        alt_units=None,
        set_occurrence_status=True,
        gen_UUID=False,
        constants={},
    )
    assert result["occurrenceStatus"] == "absent"


def test_enumerate_row_sets_occurrence_status_absent_when_negative():
    row = ("0", pd.Series({"species_A": -5, "temp": 22.5}))
    result = dataset_flipper.enumerate_row(
        row=row,
        field="species_A",
        results_column="species",
        split_fields=False,
        delimiter="_",
        split_column_name="life_stage",
        match_col_variants=False,
        primary_units=None,
        alt_units=None,
        set_occurrence_status=True,
        gen_UUID=False,
        constants={},
    )
    assert result["occurrenceStatus"] == "absent"


def test_enumerate_row_sets_occurrence_status_absent_when_nan_string():
    row = ("0", pd.Series({"species_A": "NaN", "temp": 22.5}))
    result = dataset_flipper.enumerate_row(
        row=row,
        field="species_A",
        results_column="species",
        split_fields=True,
        delimiter="_",
        split_column_name="life_stage",
        match_col_variants=False,
        primary_units="organismQuantity",
        alt_units=None,
        set_occurrence_status=True,
        gen_UUID=False,
        constants={},
    )
    assert result["occurrenceStatus"] == "absent"


def test_enumerate_row_generates_uuid_when_enabled():
    row = ("0", pd.Series({"species_A": 10, "temp": 22.5}))
    result = dataset_flipper.enumerate_row(
        row=row,
        field="species_A",
        results_column="species",
        split_fields=False,
        delimiter="_",
        split_column_name="life_stage",
        match_col_variants=False,
        primary_units=None,
        alt_units=None,
        set_occurrence_status=False,
        gen_UUID=True,
        constants={},
    )
    assert "occurrenceID" in result


def test_enumerate_row_adds_constants(mock_constants):
    row = ("0", pd.Series({"species_A": 10, "temp": 22.5}))
    result = dataset_flipper.enumerate_row(
        row=row,
        field="species_A",
        results_column="species",
        split_fields=False,
        delimiter="_",
        split_column_name="life_stage",
        match_col_variants=False,
        primary_units=None,
        alt_units=None,
        set_occurrence_status=False,
        gen_UUID=False,
        constants=mock_constants,
    )
    assert result["country"] == "US"
    assert result["project"] == "TACT"


def test_enumerate_row_no_constants(mock_constants_empty):
    row = ("0", pd.Series({"species_A": 10, "temp": 22.5}))
    result = dataset_flipper.enumerate_row(
        row=row,
        field="species_A",
        results_column="species",
        split_fields=False,
        delimiter="_",
        split_column_name="life_stage",
        match_col_variants=False,
        primary_units=None,
        alt_units=None,
        set_occurrence_status=False,
        gen_UUID=False,
        constants=mock_constants_empty,
    )
    assert "country" not in result
    assert "project" not in result


def test_enumerate_row_match_col_variants_sets_alt_units():
    row = ("0", pd.Series({"species_A": 10, "temp_alt": 25.0}))
    result = dataset_flipper.enumerate_row(
        row=row,
        field="species_A",
        results_column="species",
        split_fields=False,
        delimiter="_",
        split_column_name="life_stage",
        match_col_variants=True,
        primary_units="count",
        alt_units="temp_alt",
        set_occurrence_status=False,
        gen_UUID=False,
        constants={},
    )
    assert result["temp_alt"] == 25.0


def test_enumerate_row_split_fields_false_sets_results_to_field():
    row = ("0", pd.Series({"species_A": 10, "temp": 22.5}))
    result = dataset_flipper.enumerate_row(
        row=row,
        field="species_A",
        results_column="species",
        split_fields=False,
        delimiter="_",
        split_column_name="life_stage",
        match_col_variants=False,
        primary_units=None,
        alt_units=None,
        set_occurrence_status=False,
        gen_UUID=False,
        constants={},
    )
    assert result["species"] == "species_A"


# -- pivot --

def test_pivot_creates_columns_from_pivoted_column():
    df = pd.DataFrame({
        "station": ["A", "A", "B"],
        "species": ["sp1", "sp2", "sp1"],
        "count": [10, 20, 30],
    })
    result = dataset_flipper.pivot(df, "species", "count")
    assert "sp1" in result.columns
    assert "sp2" in result.columns


def test_pivot_preserves_non_pivot_columns():
    df = pd.DataFrame({
        "date": ["2023-01-01", "2023-01-01", "2023-01-02"],
        "species": ["sp1", "sp2", "sp1"],
        "count": [10, 20, 30],
    })
    result = dataset_flipper.pivot(df, "species", "count")
    assert "date" in result.columns


def test_pivot_raises_on_failure():
    df = pd.DataFrame({
        "species": ["sp1", "sp2"],
        "count": [10, 20],
    })
    with patch.object(df, "pivot", side_effect=Exception("pivot error")):
        with pytest.raises(Exception):
            dataset_flipper.pivot(df, "species", "count")


def test_pivot_resets_index():
    df = pd.DataFrame({
        "station": ["A", "A", "B"],
        "species": ["sp1", "sp2", "sp1"],
        "count": [10, 20, 30],
    })
    result = dataset_flipper.pivot(df, "species", "count")
    assert result.index.tolist() == [0, 1]


# -- process (dataset_flipper) --

def test_process_returns_dataframe(sample_df):
    result = dataset_flipper.process(
        target_data_columns=["species_A", "species_B"],
        results_column="species",
        df=sample_df,
        drop_units=False,
        drop_empty_records=False,
        split_fields=False,
        delimiter="_",
        split_column_name="life_stage",
        match_col_variants=False,
        primary_units=None,
        alt_units=None,
        set_occurrence_status=False,
        gen_UUID=False,
        constants={},
    )
    assert isinstance(result, pd.DataFrame)
    assert len(result) > 0


def test_process_drops_empty_records_when_enabled():
    df = pd.DataFrame({
        "date": ["2023-01-01", "2023-01-02"],
        "species_A": [0, 5],
        "species_B": [-1, 0],
    })
    result = dataset_flipper.process(
        target_data_columns=["species_A", "species_B"],
        results_column="species",
        df=df,
        drop_units=False,
        drop_empty_records=True,
        split_fields=False,
        delimiter="_",
        split_column_name="life_stage",
        match_col_variants=False,
        primary_units=None,
        alt_units=None,
        set_occurrence_status=False,
        gen_UUID=False,
        constants={},
    )
    assert isinstance(result, pd.DataFrame)


def test_process_drops_units_row_when_enabled():
    df = pd.DataFrame({
        "units": ["count", "count"],
        "species_A": [10, 5],
        "species_B": [3, 0],
    })
    result = dataset_flipper.process(
        target_data_columns=["species_A", "species_B"],
        results_column="species",
        df=df,
        drop_units=True,
        drop_empty_records=False,
        split_fields=False,
        delimiter="_",
        split_column_name="life_stage",
        match_col_variants=False,
        primary_units=None,
        alt_units=None,
        set_occurrence_status=False,
        gen_UUID=False,
        constants={},
    )
    assert isinstance(result, pd.DataFrame)


def test_process_skips_rows_with_non_numeric_values():
    df = pd.DataFrame({
        "date": ["2023-01-01", "2023-01-02"],
        "species_A": ["abc", 5],
        "species_B": [3, 0],
    })
    result = dataset_flipper.process(
        target_data_columns=["species_A", "species_B"],
        results_column="species",
        df=df,
        drop_units=False,
        drop_empty_records=True,
        split_fields=False,
        delimiter="_",
        split_column_name="life_stage",
        match_col_variants=False,
        primary_units=None,
        alt_units=None,
        set_occurrence_status=False,
        gen_UUID=False,
        constants={},
    )
    assert isinstance(result, pd.DataFrame)


def test_process_removes_target_columns_from_output():
    df = pd.DataFrame({
        "date": ["2023-01-01"],
        "species_A": [10],
        "species_B": [3],
    })
    result = dataset_flipper.process(
        target_data_columns=["species_A", "species_B"],
        results_column="species",
        df=df,
        drop_units=False,
        drop_empty_records=False,
        split_fields=False,
        delimiter="_",
        split_column_name="life_stage",
        match_col_variants=False,
        primary_units=None,
        alt_units=None,
        set_occurrence_status=False,
        gen_UUID=False,
        constants={},
    )
    assert "species_A" not in result.columns
    assert "species_B" not in result.columns


# -----------------------------------------------------------------------------
# datetime_parser
# -----------------------------------------------------------------------------

from tact.processing import datetime_parser


@pytest.fixture
def mock_csv_row():
    return {
        "year": "2023",
        "month": "01",
        "day": "15",
        "time": "1430",
    }


@pytest.fixture
def mock_date_fields():
    return {
        "year": "year",
        "month": "month",
        "day": "day",
    }


@pytest.fixture
def mock_time_fields():
    return {
        "time": "time",
    }


@pytest.fixture
def mock_dateutil_parse_fail():
    with patch("dateutil.parser.parse", side_effect=ValueError("parse failed")):
        yield


def test_create_iso_time_parses_date_and_time(mock_csv_row, mock_date_fields, mock_time_fields):
    result = datetime_parser.create_iso_time(mock_csv_row, mock_date_fields, mock_time_fields)
    assert "2023-01-15T14:30:00" in result


def test_create_iso_time_handles_8_char_time_hhmmss(mock_dateutil_parse_fail):
    row = {"year": "2023", "month": "01", "day": "15", "time": "143055"}
    fields = {"date": "year"}
    time = {"time": "time"}
    result = datetime_parser.create_iso_time(row, fields, time)
    assert "14:30:55" in result


def test_create_iso_time_handles_4_char_time(mock_dateutil_parse_fail):
    row = {"year": "2023", "month": "01", "day": "15", "time": "1430"}
    fields = {"date": "year"}
    time = {"time": "time"}
    result = datetime_parser.create_iso_time(row, fields, time)
    assert "14:30:00" in result


def test_create_iso_time_handles_3_char_time(mock_dateutil_parse_fail):
    row = {"year": "2023", "month": "01", "day": "15", "time": "143"}
    fields = {"date": "year"}
    time = {"time": "time"}
    result = datetime_parser.create_iso_time(row, fields, time)
    assert "01:43:00" in result


def test_create_iso_time_handles_1_char_time(mock_dateutil_parse_fail):
    row = {"year": "2023", "month": "01", "day": "15", "time": "1"}
    fields = {"date": "year"}
    time = {"time": "time"}
    result = datetime_parser.create_iso_time(row, fields, time)
    assert "00:01:00" in result


def test_create_iso_time_handles_8_char_time_with_seconds(mock_dateutil_parse_fail):
    row = {"year": "2023", "month": "01", "day": "15", "time": "143055"}
    fields = {"date": "year"}
    time = {"time": "time"}
    result = datetime_parser.create_iso_time(row, fields, time)
    assert "14:30:55" in result


def test_create_iso_time_handles_date_yyyymmdd_format():
    row = {"date": "20230115", "time": "1430"}
    fields = {"date": "date"}
    time = {"time": "time"}
    result = datetime_parser.create_iso_time(row, fields, time)
    assert "2023-01-15" in result


def test_create_iso_time_handles_date_mmddyyyy_format():
    row = {"date": "01152023", "time": "1430"}
    fields = {"date": "date"}
    time = {"time": "time"}
    result = datetime_parser.create_iso_time(row, fields, time)
    assert "2023-01-15" in result


def test_create_iso_time_handles_6_char_datenum():
    row = {"date": "738000", "time": "1430"}
    fields = {"date": "date"}
    time = {"time": "time"}
    result = datetime_parser.create_iso_time(row, fields, time)
    assert "T" in result


def test_create_iso_time_handles_7_char_date_starting_19(mock_dateutil_parse_fail):
    row = {"date": "1990101", "time": "1430"}
    fields = {"date": "date"}
    time = {"time": "time"}
    result = datetime_parser.create_iso_time(row, fields, time)
    assert "1990-01-01" in result


def test_create_iso_time_handles_7_char_date_starting_20(mock_dateutil_parse_fail):
    row = {"date": "2010101", "time": "1430"}
    fields = {"date": "date"}
    time = {"time": "time"}
    result = datetime_parser.create_iso_time(row, fields, time)
    assert "2010-01-01" in result


def test_create_iso_time_uses_epoch_when_date_missing(mock_dateutil_parse_fail):
    row = {"time": "1430"}
    fields = {"date": "missing"}
    time = {"time": "time"}
    result = datetime_parser.create_iso_time(row, fields, time)
    assert "1970-01-01" in result


def test_create_iso_time_handles_three_date_fields(mock_dateutil_parse_fail):
    row = {"year": "2023", "month": "01", "day": "15", "time": "1430"}
    fields = {"year": "year", "month": "month", "day": "day"}
    time = {"time": "time"}
    result = datetime_parser.create_iso_time(row, fields, time)
    assert "2023-01-15" in result


def test_create_iso_time_handles_three_time_fields(mock_dateutil_parse_fail):
    row = {"year": "2023", "month": "01", "day": "15", "hour": "14", "minute": "30", "second": "55"}
    fields = {"date": "year"}
    time = {"hour": "hour", "minute": "minute", "second": "second"}
    result = datetime_parser.create_iso_time(row, fields, time)
    assert "14:30:55" in result


def test_create_iso_time_uses_midday_when_time_missing(mock_dateutil_parse_fail):
    row = {"year": "2023", "month": "01", "day": "15"}
    fields = {"date": "year"}
    time = {"time": "missing"}
    result = datetime_parser.create_iso_time(row, fields, time)
    assert "12:00:00" in result


def test_create_iso_time_returns_iso_format(mock_csv_row, mock_date_fields, mock_time_fields):
    result = datetime_parser.create_iso_time(mock_csv_row, mock_date_fields, mock_time_fields)
    assert "T" in result


# -- compile_datetime --

def test_compile_datetime_creates_output_file(tmp_path):
    csv_content = "year,month,day,time\n2023,01,15,1430\n"
    import io
    f = io.StringIO(csv_content)

    out_path = str(tmp_path / "out.csv")
    result = datetime_parser.compile_datetime(
        f,
        out_path,
        input_date_fields={"date": "year"},
        input_time_fields={"time": "time"},
        parsed_column_name="parsed_time",
        parsed_column_position=4,
        verbose=False,
    )
    assert result is not None


def test_compile_datetime_skips_empty_rows(tmp_path):
    csv_content = "year,month,day,time\n2023,01,15,1430\n,,,,\n"
    import io
    f = io.StringIO(csv_content)

    out_path = str(tmp_path / "out.csv")
    result = datetime_parser.compile_datetime(
        f,
        out_path,
        input_date_fields={"date": "year"},
        input_time_fields={"time": "time"},
        parsed_column_name="parsed_time",
        parsed_column_position=4,
        verbose=False,
    )
    assert result is not None


# -----------------------------------------------------------------------------
# quality_checker
# -----------------------------------------------------------------------------

from tact.processing import quality_checker


@pytest.fixture
def qa_settings():
    return {"minDate": "", "maxDate": ""}


@pytest.fixture
def temp_csv(tmp_path):
    csv_path = str(tmp_path / "test_data.csv")
    df = pd.DataFrame({
        "date": ["2023-01-01", "2023-06-15", "2023-12-31"],
        "value": [1, 2, 3],
    })
    df.to_csv(csv_path, index=False)
    return csv_path


def test_pull_date_range_sets_min_date(temp_csv, qa_settings):
    with patch("pandas.read_csv") as mock_read:
        mock_read.return_value = pd.Series([
            datetime.datetime(2023, 1, 1),
            datetime.datetime(2023, 6, 15),
            datetime.datetime(2023, 12, 31),
        ])
        result = quality_checker.pull_date_range(
            input_file=temp_csv,
            date_column="date",
            date_format="%Y-%m-%d",
            qa_settings_JSON=qa_settings,
        )
    assert result["minDate"] == "2023-01-01"


def test_pull_date_range_sets_max_date(temp_csv, qa_settings):
    with patch("pandas.read_csv") as mock_read:
        mock_read.return_value = pd.Series([
            datetime.datetime(2023, 1, 1),
            datetime.datetime(2023, 6, 15),
            datetime.datetime(2023, 12, 31),
        ])
        result = quality_checker.pull_date_range(
            input_file=temp_csv,
            date_column="date",
            date_format="%Y-%m-%d",
            qa_settings_JSON=qa_settings,
        )
    assert result["maxDate"] == "2023-12-31"


def test_pull_date_range_returns_settings(qa_settings):
    assert "minDate" in qa_settings
    assert "maxDate" in qa_settings


def test_pull_date_range_returns_modified_qa_settings(temp_csv, qa_settings):
    with patch("pandas.read_csv") as mock_read:
        mock_read.return_value = pd.Series([
            datetime.datetime(2023, 1, 1),
            datetime.datetime(2023, 6, 15),
            datetime.datetime(2023, 12, 31),
        ])
        original = {"other_key": "value"}
        result = quality_checker.pull_date_range(
            input_file=temp_csv,
            date_column="date",
            date_format="%Y-%m-%d",
            qa_settings_JSON=original,
        )
    assert result["other_key"] == "value"
    assert "minDate" in result
    assert "maxDate" in result


# -----------------------------------------------------------------------------
# xml_generator
# -----------------------------------------------------------------------------

from tact.processing import xml_generator


@pytest.fixture
def mock_settings():
    return {
        "eddType": "tabledap",
        "parameters": [
            {"position": 1, "value": "--dataset"},
            {"position": 2, "value": "my_dataset"},
        ],
        "erddapPath": "/opt/erddap/",
    }


def test_compile_args_string_includes_edd_type(mock_settings):
    result = xml_generator.compile_args_string(mock_settings)
    assert "tabledap" in result


def test_compile_args_string_includes_parameters(mock_settings):
    result = xml_generator.compile_args_string(mock_settings)
    assert "--dataset" in result
    assert "my_dataset" in result


def test_compile_args_string_returns_string(mock_settings):
    result = xml_generator.compile_args_string(mock_settings)
    assert isinstance(result, str)


def test_compile_args_string_empty_parameters():
    settings = {
        "eddType": "tabledap",
        "parameters": [],
        "erddapPath": "/opt/erddap/",
    }
    result = xml_generator.compile_args_string(settings)
    assert "tabledap" in result


def test_invoke_calls_subprocess_run(mock_settings):
    with patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(stdout="ok", stderr="")
        xml_generator.invoke(mock_settings)
        mock_run.assert_called_once()


def test_invoke_constructs_java_command(mock_settings):
    with patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(stdout="ok", stderr="")
        xml_generator.invoke(mock_settings)
        call_args = mock_run.call_args[0][0]
        assert "java" in call_args
        assert any("GenerateDatasetsXml" in arg for arg in call_args)


def test_invoke_handles_exception(mock_settings, caplog):
    with patch("subprocess.run", side_effect=ValueError("test error")):
        with caplog.at_level(logging.ERROR):
            with pytest.raises(AttributeError):
                xml_generator.invoke(mock_settings)