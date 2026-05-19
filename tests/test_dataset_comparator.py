"""
Tests for tact.processing.dataset_comparator
"""

import logging
import pytest
import pandas as pd

from tact.processing import dataset_comparator


# -----------------------------------------------------------------------------
# Fixtures
# -----------------------------------------------------------------------------

@pytest.fixture
def df1() -> pd.DataFrame:
    return pd.DataFrame({
        "station": ["A", "B", "C"],
        "depth":   [10,  20,  30],
        "temp":    [15.0, 16.5, 14.0],
    })


@pytest.fixture
def df2() -> pd.DataFrame:
    return pd.DataFrame({
        "station": ["A", "B", "D"],
        "depth":   [10,  20,  40],
        "temp":    [15.1, 17.0, 13.0],
    })


# -----------------------------------------------------------------------------
# compare_schema
# -----------------------------------------------------------------------------

def test_compare_schema_shared_and_exclusive(df1, df2):
    df2_extra = df2.copy()
    df2_extra["salinity"] = [30.0, 31.0, 32.0]

    result = dataset_comparator.compare_schema(df1, df2_extra)

    assert set(result["shared_columns"]) == {"station", "depth", "temp"}
    assert result["only_in_1"] == []
    assert result["only_in_2"] == ["salinity"]
    assert any(r["column"] == "temp" for r in result["dtype_comparison"])


def test_compare_schema_all_shared(df1, df2):
    result = dataset_comparator.compare_schema(df1, df2)

    assert set(result["shared_columns"]) == {"station", "depth", "temp"}
    assert result["only_in_1"] == []
    assert result["only_in_2"] == []


def test_compare_schema_no_overlap():
    a = pd.DataFrame({"x": [1]})
    b = pd.DataFrame({"y": [2]})

    result = dataset_comparator.compare_schema(a, b)

    assert result["shared_columns"] == []
    assert result["only_in_1"] == ["x"]
    assert result["only_in_2"] == ["y"]
    assert result["dtype_comparison"] == []


# -----------------------------------------------------------------------------
# compute_coverage
# -----------------------------------------------------------------------------

def test_compute_coverage_basic(df1, df2):
    result = dataset_comparator.compute_coverage(df1, df2, key_columns=["station"])

    assert result is not None
    assert result["rows_in_1"] == 3
    assert result["rows_in_2"] == 3
    assert result["matched"] == 2    # A and B match; C vs D don't
    assert result["only_in_1"] == 1  # C
    assert result["only_in_2"] == 1  # D
    assert result["union_total"] == 4


def test_compute_coverage_full_match():
    df_a = pd.DataFrame({"id": [1, 2], "val": [10, 20]})
    df_b = pd.DataFrame({"id": [1, 2], "val": [11, 21]})

    result = dataset_comparator.compute_coverage(df_a, df_b, key_columns=["id"])

    assert result["matched"] == 2
    assert result["only_in_1"] == 0
    assert result["only_in_2"] == 0
    assert result["match_pct"] == 1.0


def test_compute_coverage_missing_key_logs_error(df1, df2, caplog):
    with caplog.at_level(logging.ERROR):
        result = dataset_comparator.compute_coverage(df1, df2, key_columns=["nonexistent"])

    assert result is None
    assert "nonexistent" in caplog.text


# -----------------------------------------------------------------------------
# _cell_matches
# -----------------------------------------------------------------------------

@pytest.mark.parametrize("tol, v1, v2, expected", [
    (None,        15.0,   15.0,                  True),
    (None,        15.0,   15.1,                  False),
    (0.5,         15.0,   15.4,                  True),
    (0.5,         15.0,   15.6,                  False),
    ("contains",  "Acartia longiremis", "Acartia", True),
    ("contains",  "Acartia",  "Calanus",          False),
    (None,        float("nan"), float("nan"),     True),
    (None,        float("nan"), 5.0,              False),
], ids=[
    "exact_match", "exact_no_match",
    "numeric_in_tol", "numeric_out_tol",
    "contains_match", "contains_no_match",
    "nan_nan_match", "nan_value_no_match",
])
def test_cell_matches_parametrized(tol, v1, v2, expected):
    assert dataset_comparator._cell_matches(v1, v2, tol) == expected


@pytest.mark.parametrize("tol_str, expected_type", [
    ("0.05",  float),
    ("1",     float),
    ("1h",    pd.Timedelta),
    ("30min", pd.Timedelta),
], ids=["float_string", "int_string", "timedelta_hours", "timedelta_minutes"])
def test_parse_tolerance_string_coercion(tol_str, expected_type):
    """Numeric strings like '0.05' must parse to float, not attempt pd.Timedelta."""
    result = dataset_comparator._parse_tolerance(tol_str)
    assert isinstance(result, expected_type), (
        f"_parse_tolerance('{tol_str}') returned {type(result).__name__}, expected {expected_type.__name__}"
    )


# -----------------------------------------------------------------------------
# merge_on_keys
# -----------------------------------------------------------------------------

def test_merge_on_keys_exact(df1, df2):
    merged = dataset_comparator.merge_on_keys(df1, df2, ["station"], ["temp"])

    assert merged is not None
    assert len(merged) == 2  # A and B
    assert "temp_1" in merged.columns
    assert "temp_2" in merged.columns


def test_merge_on_keys_missing_key_logs_error(df1, df2, caplog):
    with caplog.at_level(logging.ERROR):
        result = dataset_comparator.merge_on_keys(df1, df2, ["missing_col"], ["temp"])

    assert result is None
    assert "missing_col" in caplog.text


# -----------------------------------------------------------------------------
# build_diff_mask
# -----------------------------------------------------------------------------

def test_build_diff_mask_shape(df1, df2):
    merged = dataset_comparator.merge_on_keys(df1, df2, ["station"], ["temp"])
    mask = dataset_comparator.build_diff_mask(merged, ["temp"], {}, None, "_1", "_2")

    assert mask.shape == (len(merged), 1)
    assert "temp" in mask.columns


def test_build_diff_mask_values():
    merged = pd.DataFrame({
        "station": ["A", "B"],
        "temp_1":  [15.0, 16.5],
        "temp_2":  [15.0, 17.0],
    })
    mask = dataset_comparator.build_diff_mask(merged, ["temp"], {}, None, "_1", "_2")

    assert mask.at[0, "temp"] == True   # A: same
    assert mask.at[1, "temp"] == False  # B: differs


# -----------------------------------------------------------------------------
# build_value_diffs
# -----------------------------------------------------------------------------

def test_build_value_diffs_correct(df1, df2):
    merged = dataset_comparator.merge_on_keys(df1, df2, ["station"], ["temp"])
    mask = dataset_comparator.build_diff_mask(merged, ["temp"], {}, None, "_1", "_2")
    diffs = dataset_comparator.build_value_diffs(merged, mask, ["temp"], ["station"], "_1", "_2")

    # A: same (15.0 vs 15.1 with no tol is a diff), B: 16.5 vs 17.0 is a diff
    assert all(d["column"] == "temp" for d in diffs)
    assert all("station" in d["key_vals"] for d in diffs)


def test_build_value_diffs_max_cells():
    n = 20
    merged = pd.DataFrame({
        "id":  list(range(n)),
        "v_1": [float(i) for i in range(n)],
        "v_2": [float(i) + 1 for i in range(n)],
    })
    mask = pd.DataFrame({"v": [False] * n}, index=merged.index)
    diffs = dataset_comparator.build_value_diffs(merged, mask, ["v"], ["id"], "_1", "_2", max_cells=5)

    assert len(diffs) == 5


# -----------------------------------------------------------------------------
# build_column_summary
# -----------------------------------------------------------------------------

def test_build_column_summary_sorted():
    mask = pd.DataFrame({
        "temp": [True, True, False, False, False],  # 3 diffs (3 False values)
        "depth": [True, False, True, True, True],   # 1 diff (1 False value)
    })
    summary = dataset_comparator.build_column_summary(mask, ["temp", "depth"], {}, None, matched_count=5)

    assert summary[0]["column"] == "temp"   # more diffs first
    assert summary[0]["n_diffs"] == 3
    assert summary[1]["column"] == "depth"
    assert summary[1]["n_diffs"] == 1


# -----------------------------------------------------------------------------
# run_comparison (end-to-end)
# -----------------------------------------------------------------------------

def test_run_comparison_full(df1, df2):
    result = dataset_comparator.run_comparison(
        df1=df1, df2=df2,
        key_columns=["station"],
        compare_columns=[],
        exclude_columns=[],
        tolerances={},
        default_tolerance=None,
        label_1="Dataset 1",
        label_2="Dataset 2",
        max_diff_rows=500,
    )

    assert result is not None
    assert "schema" in result
    assert "coverage" in result
    assert "value_diffs" in result
    assert "summary" in result
    assert result["coverage"]["matched"] == 2


def test_run_comparison_missing_keys_returns_none(df1, df2, caplog):
    with caplog.at_level(logging.ERROR):
        result = dataset_comparator.run_comparison(
            df1=df1, df2=df2,
            key_columns=[],
            compare_columns=[],
            exclude_columns=[],
            tolerances={},
            default_tolerance=None,
            label_1="D1",
            label_2="D2",
            max_diff_rows=500,
        )

    assert result is None
    assert "key_columns" in caplog.text


def test_run_comparison_with_tolerance(df1, df2):
    # temp differs by 0.5 for B (16.5 vs 17.0) — within tol 0.6 should pass
    result = dataset_comparator.run_comparison(
        df1=df1, df2=df2,
        key_columns=["station"],
        compare_columns=["temp"],
        exclude_columns=[],
        tolerances={"temp": 0.6},
        default_tolerance=None,
        label_1="D1",
        label_2="D2",
        max_diff_rows=500,
    )

    assert result is not None
    # A: 15.0 vs 15.1 (diff 0.1 ≤ 0.6 → match), B: 16.5 vs 17.0 (diff 0.5 ≤ 0.6 → match)
    assert result["summary"]["rows_with_diffs"] == 0
