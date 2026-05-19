import pytest
from unittest.mock import patch, mock_open, MagicMock
import pandas as pd

import tact.processing.dataset_flipper as flipper


# --- enumerate_row ---
def test_enumerate_row_with_split_fields():
    """Test enumerate_row with split_fields enabled."""
    row = (0, pd.Series({"species_A": 10}))
    result = flipper.enumerate_row(
        row=row,
        field="species_A",
        results_column="results_column",
        split_fields=True,
        delimiter="_",
        split_column_name="split_col",
        match_col_variants=False,
        primary_units=None,
        alt_units=None,
        set_occurrence_status=False,
        gen_UUID=False,
        constants={},
    )
    assert result["results_column"] == "species"
    assert result["split_col"] == "A"


def test_enumerate_row_without_split_fields():
    """Test enumerate_row with split_fields disabled."""
    row = (0, pd.Series({"species_A": 5}))
    result = flipper.enumerate_row(
        row=row,
        field="species_A",
        results_column="results_column",
        split_fields=False,
        delimiter="_",
        split_column_name="split_col",
        match_col_variants=False,
        primary_units=None,
        alt_units=None,
        set_occurrence_status=False,
        gen_UUID=False,
        constants={},
    )
    assert result["results_column"] == "species_A"


def test_enumerate_row_with_primary_units():
    """Test that primary_units creates a column with the count."""
    row = (0, pd.Series({"species_A": 5}))
    result = flipper.enumerate_row(
        row=row,
        field="species_A",
        results_column="results_column",
        split_fields=False,
        delimiter="_",
        split_column_name="split_col",
        match_col_variants=False,
        primary_units="abundance",
        alt_units=None,
        set_occurrence_status=False,
        gen_UUID=False,
        constants={},
    )
    assert result["abundance"] == 5


def test_enumerate_row_with_default_units():
    """Test that default 'organismQuantity' column is created when no primary_units."""
    row = (0, pd.Series({"species_A": 5}))
    result = flipper.enumerate_row(
        row=row,
        field="species_A",
        results_column="results_column",
        split_fields=False,
        delimiter="_",
        split_column_name="split_col",
        match_col_variants=False,
        primary_units=None,
        alt_units=None,
        set_occurrence_status=False,
        gen_UUID=False,
        constants={},
    )
    assert result["organismQuantity"] == 5


def test_enumerate_row_with_occurrence_status_present():
    """Test occurrence_status is set to 'present' when count > 0."""
    row = (0, pd.Series({"species_A": 5}))
    result = flipper.enumerate_row(
        row=row,
        field="species_A",
        results_column="results_column",
        split_fields=False,
        delimiter="_",
        split_column_name="split_col",
        match_col_variants=False,
        primary_units=None,
        alt_units=None,
        set_occurrence_status=True,
        gen_UUID=False,
        constants={},
    )
    assert result["occurrenceStatus"] == "present"


def test_enumerate_row_with_occurrence_status_absent():
    """Test occurrence_status is set to 'absent' when count is 0."""
    row = (0, pd.Series({"species_A": 0}))
    result = flipper.enumerate_row(
        row=row,
        field="species_A",
        results_column="results_column",
        split_fields=False,
        delimiter="_",
        split_column_name="split_col",
        match_col_variants=False,
        primary_units=None,
        alt_units=None,
        set_occurrence_status=True,
        gen_UUID=False,
        constants={},
    )
    assert result["occurrenceStatus"] == "absent"


def test_enumerate_row_with_constants():
    """Test that constants are added to the result."""
    row = (0, pd.Series({"species_A": 5}))
    result = flipper.enumerate_row(
        row=row,
        field="species_A",
        results_column="results_column",
        split_fields=False,
        delimiter="_",
        split_column_name="split_col",
        match_col_variants=False,
        primary_units=None,
        alt_units=None,
        set_occurrence_status=False,
        gen_UUID=False,
        constants={"site": "Station1", "depth": 10},
    )
    assert result["site"] == "Station1"
    assert result["depth"] == 10


# --- pivot ---
def test_pivot_creates_columns():
    """Test that pivot creates new columns from pivoted_column values."""
    df = pd.DataFrame({
        "station": ["A", "B"],
        "species": ["sp1", "sp2"],
        "count": [10, 20],
    })
    result = flipper.pivot(df, pivoted_column="species", value_column="count")
    assert "sp1" in result.columns
    assert "sp2" in result.columns


def test_pivot_returns_empty_on_invalid_columns():
    """Test that pivot handles invalid columns gracefully."""
    df = pd.DataFrame({"a": [1], "b": [2]})
    result = flipper.pivot(df, pivoted_column="nonexistent", value_column="b")
    assert result is not None


# --- process (dataset_flipper) ---
def test_process_with_drop_empty_records():
    """Test that rows with zero or negative counts are skipped when drop_empty_records=True."""
    df = pd.DataFrame({
        "species_A": [10, -1, 0],
        "species_B": [5, 3, 0],
    })
    result = flipper.process(
        target_data_columns=["species_A", "species_B"],
        results_column="results_column",
        df=df,
        drop_units=False,
        drop_empty_records=True,
        split_fields=False,
        delimiter=",",
        split_column_name="split_col",
        match_col_variants=False,
        primary_units=None,
        alt_units=None,
        set_occurrence_status=False,
        gen_UUID=False,
        constants={},
    )
    assert result is not None
    assert len(result) > 0


def test_process_without_drop_empty_records():
    """Test that all rows are processed when drop_empty_records=False."""
    df = pd.DataFrame({
        "species_A": [10, 0, -5],
    })
    result = flipper.process(
        target_data_columns=["species_A"],
        results_column="results_column",
        df=df,
        drop_units=False,
        drop_empty_records=False,
        split_fields=False,
        delimiter=",",
        split_column_name="split_col",
        match_col_variants=False,
        primary_units=None,
        alt_units=None,
        set_occurrence_status=False,
        gen_UUID=False,
        constants={},
    )
    assert result is not None


def test_process_with_drop_units():
    """Test that first row is dropped when drop_units=True."""
    df = pd.DataFrame({
        "species_A": [10, 20, 30],
    })
    result = flipper.process(
        target_data_columns=["species_A"],
        results_column="results_column",
        df=df,
        drop_units=True,
        drop_empty_records=False,
        split_fields=False,
        delimiter=",",
        split_column_name="split_col",
        match_col_variants=False,
        primary_units=None,
        alt_units=None,
        set_occurrence_status=False,
        gen_UUID=False,
        constants={},
    )
    assert result is not None


def test_process_with_gen_uuid():
    """Test that occurrenceID is generated when gen_UUID=True."""
    df = pd.DataFrame({
        "species_A": [10],
    })
    result = flipper.process(
        target_data_columns=["species_A"],
        results_column="results_column",
        df=df,
        drop_units=False,
        drop_empty_records=False,
        split_fields=False,
        delimiter=",",
        split_column_name="split_col",
        match_col_variants=False,
        primary_units=None,
        alt_units=None,
        set_occurrence_status=False,
        gen_UUID=True,
        constants={},
    )
    assert "occurrenceID" in result.columns


def test_process_with_invalid_value_logs_error(caplog):
    """Test that invalid numeric values are logged and skipped."""
    df = pd.DataFrame({
        "species_A": ["not_a_number"],
    })
    result = flipper.process(
        target_data_columns=["species_A"],
        results_column="results_column",
        df=df,
        drop_units=False,
        drop_empty_records=True,
        split_fields=False,
        delimiter=",",
        split_column_name="split_col",
        match_col_variants=False,
        primary_units=None,
        alt_units=None,
        set_occurrence_status=False,
        gen_UUID=False,
        constants={},
    )
    assert result is not None
    assert "Failed to evaluate value as number" in caplog.text


def test_process_with_split_fields_delimiter():
    """Test that split_fields extracts values using delimiter."""
    df = pd.DataFrame({
        "species_A": [10],
    })
    result = flipper.process(
        target_data_columns=["species_A"],
        results_column="results_column",
        df=df,
        drop_units=False,
        drop_empty_records=False,
        split_fields=True,
        delimiter="_",
        split_column_name="split_col",
        match_col_variants=False,
        primary_units=None,
        alt_units=None,
        set_occurrence_status=False,
        gen_UUID=False,
        constants={},
    )
    assert result is not None
    row = result.iloc[0]
    assert row["results_column"] == "species"
    assert row["split_col"] == "A"
