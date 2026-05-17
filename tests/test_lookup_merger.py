"""
Gold Standard Example Test for TACT Backend Logic.

This test file demonstrates best practices for writing tests in this project:
1. Arrange, Act, Assert (AAA) visual separation.
2. The use of @pytest.fixture for reusable mock data setups.
3. The use of @pytest.mark.parametrize for testing multiple scenarios cleanly.
4. Using 'caplog' to assert that error logging is working properly.
"""

import logging
import pytest
import pandas as pd
from unittest.mock import patch

# The module under test
from tact.processing import lookup_merger


# -----------------------------------------------------------------------------
# Fixtures (The "Arrange" phase for shared data)
# -----------------------------------------------------------------------------

@pytest.fixture
def target_data() -> pd.DataFrame:
    """Provides a basic target DataFrame for testing."""
    return pd.DataFrame({
        "station_id": ["A1", "B2", "C3", "D4"],
        "temperature": [22.1, 23.4, 19.8, 20.0],
    })

@pytest.fixture
def lookup_data() -> pd.DataFrame:
    """Provides a basic lookup DataFrame for testing."""
    return pd.DataFrame({
        "id_code": ["A1", "C3", "X9"],
        "region": ["North", "South", "East"],
        "depth": [10, 20, 50]
    })


# -----------------------------------------------------------------------------
# Tests (Act & Assert)
# -----------------------------------------------------------------------------

def test_merge_matched_records_success(target_data, lookup_data, caplog):
    """
    Test that a valid merge correctly joins data and keeps left rows.
    """
    # -- Arrange --
    # We want to pull 'region' and 'depth' into the target using the ID keys.
    target_key = "station_id"
    lookup_key = "id_code"
    value_columns = ["id_code", "region", "depth"] # id_code needed for the merge key
    
    # -- Act --
    # Capture logs at INFO level and above
    with caplog.at_level(logging.INFO):
        result_df = lookup_merger.merge_matched_records(
            target_df=target_data,
            lookup_df=lookup_data,
            target_key=target_key,
            lookup_key=lookup_key,
            value_columns=value_columns
        )
    
    # -- Assert --
    # 1. Output Validation
    assert result_df is not None
    assert len(result_df) == 4  # Left join preserves target row count
    
    # Station A1 should have matched data
    a1_row = result_df[result_df["station_id"] == "A1"].iloc[0]
    assert a1_row["region"] == "North"
    assert a1_row["depth"] == 10
    
    # Station B2 should have NaN for lookup columns since it wasn't in the lookup table
    b2_row = result_df[result_df["station_id"] == "B2"].iloc[0]
    assert pd.isna(b2_row["region"])
    
    # 2. Observability Validation
    assert "Merging matched records on station_id in target and id_code in lookup." in caplog.text
    assert "Merge Successful." in caplog.text


# -----------------------------------------------------------------------------
# Parametrized Tests for Edge Cases
# -----------------------------------------------------------------------------

@pytest.mark.parametrize(
    "bad_target_key, bad_lookup_key, bad_value_cols, expected_log_msg",
    [
        # Scenario 1: Target key is missing
        ("missing_key", "id_code", ["id_code", "region"], "target_key 'missing_key' not found"),
        
        # Scenario 2: Lookup key is missing
        ("station_id", "missing_key", ["missing_key", "region"], "lookup_key 'missing_key' not found"),
        
        # Scenario 3: A requested value column is missing
        ("station_id", "id_code", ["id_code", "fake_col"], "value_columns not found in lookup: ['fake_col']"),
    ],
    ids=[
        "missing_target_key",
        "missing_lookup_key",
        "missing_value_columns"
    ]
)
def test_merge_matched_records_missing_columns(
    target_data, lookup_data, caplog, 
    bad_target_key, bad_lookup_key, bad_value_cols, expected_log_msg
):
    """
    Test that missing columns elegantly abort the merge and log a specific error.
    Utilizes parameterization to test 3 different error states without code duplication.
    """
    # -- Arrange -- 
    # Handled by fixtures and parameters
    
    # -- Act --
    with caplog.at_level(logging.ERROR):
        result = lookup_merger.merge_matched_records(
            target_df=target_data,
            lookup_df=lookup_data,
            target_key=bad_target_key,
            lookup_key=bad_lookup_key,
            value_columns=bad_value_cols
        )
    
    # -- Assert --
    assert result is None
    assert expected_log_msg in caplog.text


def test_merge_matched_records_exception_handling(target_data, lookup_data, caplog):
    """
    Test that unexpected runtime exceptions during the Pandas merge are caught
    and logged, preventing application crashes.
    """
    # -- Arrange --
    # We pass valid DataFrames so the initial column validation succeeds, 
    # but we mock pd.merge to artificially simulate a runtime exception.
    
    # -- Act --
    with patch("pandas.merge", side_effect=Exception("Artificially induced merge failure")):
        with caplog.at_level(logging.ERROR):
            result = lookup_merger.merge_matched_records(
                target_df=target_data,
                lookup_df=lookup_data,
                target_key="station_id",
                lookup_key="id_code",
                value_columns=["id_code", "region"]
            )
        
    # -- Assert --
    assert result is None
    assert "Merge FAILED. Something has gone horribly awry!" in caplog.text
