import pytest
import pandas as pd
import os
import tempfile
from unittest.mock import patch, mock_open, MagicMock

from tact.util import csv_utils


# -----------------------------------------------------------------------------
# get_duplicate_columns
# -----------------------------------------------------------------------------

def test_get_duplicate_columns_returns_indices():
    """Test that duplicate column detection returns correct indices for same-name, same-data columns."""
    df = pd.DataFrame([[1, 4, 1], [2, 5, 2], [3, 6, 3]])
    df.columns = ["A", "B", "A"]  # same name AND same data — simulates repeated CSV header
    indices = csv_utils.get_duplicate_columns(df)
    assert 2 in indices


def test_get_duplicate_columns_no_duplicates():
    """Test when there are no duplicate columns."""
    df = pd.DataFrame({"A": [1, 2], "B": [3, 4], "C": [5, 6]})
    indices = csv_utils.get_duplicate_columns(df)
    assert indices == []


def test_get_duplicate_columns_marks_with_DUPE_suffix():
    """Test that duplicate columns (same name and data) get _DUPE suffix."""
    df = pd.DataFrame([[1, 4, 1], [2, 5, 2], [3, 6, 3]])
    df.columns = ["A", "B", "A"]  # same name AND same data — simulates repeated CSV header
    csv_utils.get_duplicate_columns(df)
    assert "A_DUPE" in df.columns


# -----------------------------------------------------------------------------
# drop_duplicate_columns
# -----------------------------------------------------------------------------

def test_drop_duplicate_columns_removes_duplicates():
    """Test that duplicate columns are removed."""
    df = pd.DataFrame({
        "A": [1, 2, 3],
        "B": [4, 5, 6],
        "C": [1, 2, 3],  # duplicate of A
    })
    csv_utils.drop_duplicate_columns(df, "utf-8")
    assert "C_DUPE" not in df.columns


# -----------------------------------------------------------------------------
# drop_unnamed_columns
# -----------------------------------------------------------------------------

def test_drop_unnamed_columns_removes_all_nan_columns():
    """Test that columns with all NaN values are removed."""
    df = pd.DataFrame({
        "A": [1, 2, 3],
        "B": [None, None, None],
        "C": [4, 5, 6],
    })
    csv_utils.drop_unnamed_columns(df)
    assert "B" not in df.columns


def test_drop_unnamed_columns_keeps_non_empty_columns():
    """Test that columns with at least one non-null value are kept."""
    df = pd.DataFrame({
        "A": [1, 2, 3],
        "B": [None, 5, None],
        "C": [None, None, None],
    })
    csv_utils.drop_unnamed_columns(df)
    assert "A" in df.columns
    assert "B" in df.columns
    assert "C" not in df.columns


# -----------------------------------------------------------------------------
# replace_char_in_headers
# -----------------------------------------------------------------------------

def test_replace_char_in_headers_replaces_spaces():
    """Test that spaces and underscores are replaced with spaces then with replacement char."""
    df = pd.DataFrame({
        "some column": [1, 2],
        "another_col": [3, 4],
    })
    csv_utils.replace_char_in_headers(df, " ", "_")
    assert "some_column" in df.columns
    assert "another_col" in df.columns


def test_replace_char_in_headers_replaces_multiple_spaces():
    """Test that multiple consecutive spaces are collapsed."""
    df = pd.DataFrame({
        "a  b": [1],
        "c__d": [2],
    })
    csv_utils.replace_char_in_headers(df, " ", "_")
    assert "a_b" in df.columns
    assert "c_d" in df.columns


# -----------------------------------------------------------------------------
# append_row_header
# -----------------------------------------------------------------------------

def test_append_row_header_appends_to_columns():
    """Test that row values are appended to column names."""
    df = pd.DataFrame({
        "col1": ["value_a", 10, 20],
        "col2": ["value_b", 30, 40],
    })
    csv_utils.append_row_header(df, row_index=0)
    assert "col1_value_a" in df.columns
    assert "col2_value_b" in df.columns


def test_append_row_header_skips_empty_values():
    """Test that empty or null values keep original column name."""
    df = pd.DataFrame({
        "col1": [None, 10, 20],
        "col2": ["", 30, 40],
    })
    csv_utils.append_row_header(df, row_index=0)
    assert "col1" in df.columns
    assert "col2" in df.columns


def test_append_row_header_with_drop_row():
    """Test that the appended row is dropped when drop_row=True."""
    df = pd.DataFrame({
        "col1": ["value_a", 10, 20],
        "col2": ["value_b", 30, 40],
    })
    csv_utils.append_row_header(df, row_index=0, drop_row=True)
    assert len(df) == 2


def test_append_row_header_empty_dataframe():
    """Test that empty DataFrame is returned unchanged."""
    df = pd.DataFrame()
    result = csv_utils.append_row_header(df, row_index=0)
    assert result is df


def test_append_row_header_index_out_of_range():
    """Test when row_index exceeds DataFrame height."""
    df = pd.DataFrame({"col1": [1], "col2": [2]})
    result = csv_utils.append_row_header(df, row_index=10)
    assert result is df


# -----------------------------------------------------------------------------
# replace_in_rows
# -----------------------------------------------------------------------------

def test_replace_in_rows_all_columns():
    """Test replacing a value across all columns."""
    df = pd.DataFrame({"A": [1, "old", 3], "B": ["old", 5, 6]})
    csv_utils.replace_in_rows(df, "old", "new")
    assert (df == "new").sum().sum() == 2  # 2 "old" values exist: A[1] and B[0]


def test_replace_in_rows_target_columns():
    """Test replacing a value only in specified columns."""
    df = pd.DataFrame({"A": [1, "old", 3], "B": ["old", 5, 6]})
    csv_utils.replace_in_rows(df, "old", "new", target_columns=["A"])
    assert df.loc[1, "A"] == "new"   # "old" is at row 1 in column A
    assert df.loc[0, "B"] == "old"   # column B not in target_columns, not replaced


def test_replace_in_rows_target_columns_empty_list():
    """Test that empty target_columns list replaces all columns."""
    df = pd.DataFrame({"A": [1, "old", 3], "B": ["old", 5, 6]})
    csv_utils.replace_in_rows(df, "old", "new", target_columns=[])
    assert (df == "new").sum().sum() == 2  # 2 "old" values exist: A[1] and B[0]


def test_replace_in_rows_with_nan_replacement():
    """Test that NaN values are filled with replacement value."""
    df = pd.DataFrame({"A": [1, None, 3], "B": [None, 5, 6]})
    csv_utils.replace_in_rows(df, None, "filled")
    assert df.isna().sum().sum() == 0


# -----------------------------------------------------------------------------
# delete_columns
# -----------------------------------------------------------------------------

def test_delete_columns_removes_specified_columns():
    """Test that specified columns are deleted."""
    df = pd.DataFrame({"A": [1, 2], "B": [3, 4], "C": [5, 6]})
    csv_utils.delete_columns(df, ["A", "C"])
    assert list(df.columns) == ["B"]


# -----------------------------------------------------------------------------
# write_out_data_frame
# -----------------------------------------------------------------------------

def test_write_out_data_frame_creates_file(tmp_path):
    """Test that DataFrame is written to CSV file."""
    df = pd.DataFrame({"A": [1, 2], "B": [3, 4]})
    out_path = tmp_path / "out.csv"
    csv_utils.write_out_data_frame(df, str(out_path), "utf-8")
    assert out_path.exists()
    read_df = pd.read_csv(out_path)
    assert list(read_df.columns) == ["A", "B"]


# -----------------------------------------------------------------------------
# concat_input_files
# -----------------------------------------------------------------------------

def test_concat_input_files_from_list(tmp_path):
    """Test concatenating a list of DataFrames."""
    df1 = pd.DataFrame({"A": [1, 2]})
    df2 = pd.DataFrame({"A": [3, 4]})
    out_path = str(tmp_path / "combined.csv")
    result = csv_utils.concat_input_files([df1, df2], "utf-8", out_path)
    assert result == out_path
    combined = pd.read_csv(out_path)
    assert len(combined) == 4


def test_concat_input_files_removes_duplicates(tmp_path):
    """Test that duplicate rows are removed."""
    df1 = pd.DataFrame({"A": [1, 2]})
    df2 = pd.DataFrame({"A": [2, 3]})  # 2 is duplicated
    out_path = str(tmp_path / "deduped.csv")
    csv_utils.concat_input_files([df1, df2], "utf-8", out_path)
    combined = pd.read_csv(out_path)
    assert len(combined) == 3


# -----------------------------------------------------------------------------
# merge_grouped_rows
# -----------------------------------------------------------------------------

def test_merge_grouped_rows_combines_different_rows():
    """Test that rows with different values get combined with prefix."""
    group_df = pd.DataFrame({
        "key": ["A", "A"],
        "val1": [1, 1],
        "val2": ["x", "y"],
    })
    result = csv_utils.merge_grouped_rows(group_df, append_prefix="ADDED_")
    assert "ADDED_val2" in result.columns


# -----------------------------------------------------------------------------
# sort_by_time
# -----------------------------------------------------------------------------

def test_sort_by_time_with_matching_field():
    """Test sorting by a time field that exists in columns."""
    df = pd.DataFrame({
        "time_col": [3, 1, 2],
        "results_column": ["a", "b", "c"],
    })
    result = csv_utils.sort_by_time(df, time_fields=["time_col"])
    assert list(result["time_col"]) == [1, 2, 3]


def test_sort_by_time_with_regex_match():
    """Test sorting by a field that matches date/time regex."""
    df = pd.DataFrame({
        "Date_col": [3, 1, 2],
        "results_column": ["a", "b", "c"],
    })
    result = csv_utils.sort_by_time(df, time_fields=["date_col"])
    assert list(result["Date_col"]) == [1, 2, 3]


def test_sort_by_time_no_valid_field_raises():
    """Test that ValueError is raised when no valid time field exists."""
    df = pd.DataFrame({
        "col_a": [3, 1, 2],
        "col_b": ["a", "b", "c"],
    })
    with pytest.raises(ValueError, match="No valid time field found"):
        csv_utils.sort_by_time(df, time_fields=["nonexistent"])


# -----------------------------------------------------------------------------
# combine_rows
# -----------------------------------------------------------------------------

def test_combine_rows_groups_by_match_columns():
    """Test that rows are grouped by match columns."""
    df = pd.DataFrame({
        "key": ["A", "A", "B"],
        "val": [1, 2, 3],
    })
    result = csv_utils.combine_rows(df, match_columns=["key"])
    assert result is not None
