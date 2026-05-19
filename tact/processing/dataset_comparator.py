import re
import pandas as pd
from typing import Dict, List, Optional, Union
from tact.control.logging_controller import LoggingController as loggingController

logger = loggingController.get_logger(__name__)

Tolerance = Union[float, int, str, None]


def _parse_tolerance(tol: Tolerance) -> Tolerance:
    if tol is None or isinstance(tol, (int, float)):
        return tol
    if tol == "contains":
        return tol
    if isinstance(tol, str):
        try:
            return float(tol)
        except ValueError:
            pass
        try:
            return pd.Timedelta(tol)
        except ValueError:
            logger.warning(f"Unrecognised tolerance string: '{tol}'. Using exact match fallback.")
            return tol
    return tol


def _cell_matches(v1, v2, tol: Tolerance) -> bool:
    try:
        if pd.isna(v1) and pd.isna(v2):
            return True
        if pd.isna(v1) or pd.isna(v2):
            return False
    except (TypeError, ValueError):
        pass

    if tol is None:
        return v1 == v2

    if tol == "contains":
        return str(v1).strip() in str(v2).strip() or str(v2).strip() in str(v1).strip()

    if isinstance(tol, pd.Timedelta):
        try:
            return abs(pd.to_datetime(v1, utc=True) - pd.to_datetime(v2, utc=True)) <= tol
        except Exception:
            return v1 == v2

    if isinstance(tol, (int, float)):
        try:
            return abs(float(v1) - float(v2)) <= tol
        except (TypeError, ValueError):
            return v1 == v2

    return v1 == v2


def compare_schema(
    df1: pd.DataFrame,
    df2: pd.DataFrame,
    label_1: str = "Dataset 1",
    label_2: str = "Dataset 2",
) -> Dict:
    cols1 = set(df1.columns)
    cols2 = set(df2.columns)
    shared = sorted(cols1 & cols2)
    only_in_1 = sorted(cols1 - cols2)
    only_in_2 = sorted(cols2 - cols1)

    dtype_comparison = []
    for col in shared:
        d1 = str(df1[col].dtype)
        d2 = str(df2[col].dtype)
        dtype_comparison.append({
            "column": col,
            "dtype_1": d1,
            "dtype_2": d2,
            "match": d1 == d2,
        })

    return {
        "shared_columns": shared,
        "only_in_1": only_in_1,
        "only_in_2": only_in_2,
        "dtype_comparison": dtype_comparison,
    }


def compute_coverage(
    df1: pd.DataFrame,
    df2: pd.DataFrame,
    key_columns: List[str],
    label_1: str = "Dataset 1",
    label_2: str = "Dataset 2",
    sample_limit: int = 20,
) -> Optional[Dict]:
    missing_in_1 = [k for k in key_columns if k not in df1.columns]
    missing_in_2 = [k for k in key_columns if k not in df2.columns]
    if missing_in_1:
        logger.error(f"Key column(s) {missing_in_1} not found in {label_1}.")
        return None
    if missing_in_2:
        logger.error(f"Key column(s) {missing_in_2} not found in {label_2}.")
        return None

    dup_keys_1 = int(df1.duplicated(subset=key_columns).sum())
    dup_keys_2 = int(df2.duplicated(subset=key_columns).sum())

    df1_dedup = df1.drop_duplicates(subset=key_columns)
    df2_dedup = df2.drop_duplicates(subset=key_columns)

    keys1 = set(df1_dedup[key_columns].itertuples(index=False, name=None))
    keys2 = set(df2_dedup[key_columns].itertuples(index=False, name=None))

    matched_keys = keys1 & keys2
    only1_keys = keys1 - keys2
    only2_keys = keys2 - keys1

    matched = len(matched_keys)
    only_in_1 = len(only1_keys)
    only_in_2 = len(only2_keys)
    union_total = len(keys1 | keys2)
    match_pct = round(matched / union_total, 4) if union_total > 0 else 0.0

    key_stats = []
    for k in key_columns:
        key_stats.append({
            "key_column": k,
            "unique_1": int(df1_dedup[k].nunique()),
            "total_1": len(df1),
            "unique_2": int(df2_dedup[k].nunique()),
            "total_2": len(df2),
        })

    def _rows_for_keys(df, key_set, limit):
        row_tuples = list(df[key_columns].itertuples(index=False, name=None))
        mask = pd.Series(row_tuples, index=df.index).isin(key_set)
        return df[mask].head(limit)[key_columns].to_dict(orient="records")

    sample_only_in_1 = _rows_for_keys(df1_dedup, only1_keys, sample_limit)
    sample_only_in_2 = _rows_for_keys(df2_dedup, only2_keys, sample_limit)

    return {
        "key_columns": key_columns,
        "rows_in_1": len(df1),
        "rows_in_2": len(df2),
        "matched": matched,
        "only_in_1": only_in_1,
        "only_in_2": only_in_2,
        "union_total": union_total,
        "match_pct": match_pct,
        "duplicate_keys_1": dup_keys_1,
        "duplicate_keys_2": dup_keys_2,
        "key_stats": key_stats,
        "sample_only_in_1": sample_only_in_1,
        "sample_only_in_2": sample_only_in_2,
    }


def merge_on_keys(
    df1: pd.DataFrame,
    df2: pd.DataFrame,
    key_columns: List[str],
    compare_cols: List[str],
    suffix_1: str = "_1",
    suffix_2: str = "_2",
) -> Optional[pd.DataFrame]:
    missing_in_1 = [k for k in key_columns if k not in df1.columns]
    missing_in_2 = [k for k in key_columns if k not in df2.columns]
    if missing_in_1:
        logger.error(f"Key column(s) {missing_in_1} not found in left DataFrame.")
        return None
    if missing_in_2:
        logger.error(f"Key column(s) {missing_in_2} not found in right DataFrame.")
        return None

    cols_to_select_1 = list(dict.fromkeys(key_columns + compare_cols))
    cols_to_select_2 = list(dict.fromkeys(key_columns + compare_cols))

    cols_to_select_1 = [c for c in cols_to_select_1 if c in df1.columns]
    cols_to_select_2 = [c for c in cols_to_select_2 if c in df2.columns]

    try:
        merged = pd.merge(
            df1[cols_to_select_1].drop_duplicates(subset=key_columns),
            df2[cols_to_select_2].drop_duplicates(subset=key_columns),
            on=key_columns,
            suffixes=(suffix_1, suffix_2),
            how="inner",
        )
    except Exception as e:
        logger.error(f"merge_on_keys failed: {e}")
        return None

    if merged.empty:
        logger.warning("merge_on_keys produced an empty result — no matching keys found.")

    return merged


def build_diff_mask(
    merged: pd.DataFrame,
    compare_cols: List[str],
    tolerances: Dict[str, Tolerance],
    default_tolerance: Tolerance,
    suffix_1: str,
    suffix_2: str,
) -> pd.DataFrame:
    mask_dict = {}
    for col in compare_cols:
        col1 = col + suffix_1
        col2 = col + suffix_2
        if col1 not in merged.columns or col2 not in merged.columns:
            continue
        tol = _parse_tolerance(tolerances.get(col, default_tolerance))
        mask_dict[col] = [
            _cell_matches(v1, v2, tol) 
            for v1, v2 in zip(merged[col1], merged[col2])
        ]
    return pd.DataFrame(mask_dict, index=merged.index)


def build_value_diffs(
    merged: pd.DataFrame,
    diff_mask: pd.DataFrame,
    compare_cols: List[str],
    key_columns: List[str],
    suffix_1: str,
    suffix_2: str,
    max_cells: int = 500,
) -> List[Dict]:
    records = []
    for idx, row in merged.iterrows():
        if len(records) >= max_cells:
            break
        key_vals = {k: row[k] for k in key_columns if k in row.index}
        for col in compare_cols:
            if col not in diff_mask.columns:
                continue
            if not diff_mask.at[idx, col]:
                records.append({
                    "key_vals": key_vals,
                    "column": col,
                    "value_1": row.get(col + suffix_1),
                    "value_2": row.get(col + suffix_2),
                })
                if len(records) >= max_cells:
                    break
    return records


def build_column_summary(
    diff_mask: pd.DataFrame,
    compare_cols: List[str],
    tolerances: Dict[str, Tolerance],
    default_tolerance: Tolerance,
    matched_count: int,
) -> List[Dict]:
    summary = []
    for col in compare_cols:
        if col not in diff_mask.columns:
            continue
        n_matches = int(diff_mask[col].sum())
        n_diffs = matched_count - n_matches
        pct_match = round(100.0 * n_matches / matched_count, 2) if matched_count > 0 else 0.0
        summary.append({
            "column": col,
            "tolerance": tolerances.get(col, default_tolerance),
            "matched_rows": n_matches,
            "n_diffs": n_diffs,
            "pct_match": pct_match,
        })
    summary.sort(key=lambda x: x["n_diffs"], reverse=True)
    return summary


def run_comparison(
    df1: pd.DataFrame,
    df2: pd.DataFrame,
    key_columns: List[str],
    compare_columns: List[str],
    exclude_columns: List[str],
    tolerances: Dict[str, Tolerance],
    default_tolerance: Tolerance,
    label_1: str,
    label_2: str,
    max_diff_rows: int,
) -> Optional[Dict]:
    if not key_columns:
        logger.error("key_columns must be specified to run a comparison.")
        return None

    logger.info(f"Comparing schema. df1: {len(df1)} rows, df2: {len(df2)} rows.")
    schema = compare_schema(df1, df2, label_1, label_2)
    logger.info(f"Schema: {len(schema['shared_columns'])} shared columns, "
                f"{len(schema['only_in_1'])} only in 1, {len(schema['only_in_2'])} only in 2.")

    shared = schema["shared_columns"]
    if compare_columns:
        effective_compare_cols = [c for c in compare_columns if c in shared and c not in key_columns]
    else:
        effective_compare_cols = [c for c in shared if c not in key_columns and c not in exclude_columns]
    logger.info(f"Effective compare columns ({len(effective_compare_cols)}): {effective_compare_cols}")

    logger.info("Computing row coverage.")
    coverage = compute_coverage(df1, df2, key_columns, label_1, label_2)
    if coverage is None:
        return None
    logger.info(f"Coverage: {coverage['matched']} matched, {coverage['only_in_1']} only in 1, "
                f"{coverage['only_in_2']} only in 2.")

    suffix_1, suffix_2 = "_1", "_2"
    logger.info("Merging on keys.")
    merged = merge_on_keys(df1, df2, key_columns, effective_compare_cols, suffix_1, suffix_2)

    if merged is None or merged.empty:
        logger.info("No matched rows to diff.")
        value_diffs = []
        col_summary = []
        matched_count = 0
        differing_cells = 0
        rows_with_diffs = 0
    else:
        matched_count = len(merged)
        logger.info(f"Building diff mask for {matched_count} matched rows.")
        diff_mask = build_diff_mask(merged, effective_compare_cols, tolerances, default_tolerance, suffix_1, suffix_2)
        logger.info("Building value diffs.")
        value_diffs = build_value_diffs(merged, diff_mask, effective_compare_cols, key_columns, suffix_1, suffix_2, max_cells=max_diff_rows)
        logger.info("Building column summary.")
        col_summary = build_column_summary(diff_mask, effective_compare_cols, tolerances, default_tolerance, matched_count)

        # Calculate full metrics directly from the untruncated boolean mask
        if not diff_mask.empty:
            differing_cells = int((~diff_mask).sum().sum())
            rows_with_diffs = int((~diff_mask).any(axis=1).sum())
        else:
            differing_cells = 0
            rows_with_diffs = 0

    total_cells = matched_count * len(effective_compare_cols) if effective_compare_cols else 0
    identical_matched_rows = matched_count - rows_with_diffs
    overall_match_pct = round(100.0 * (total_cells - differing_cells) / total_cells, 2) if total_cells > 0 else 100.0

    return {
        "schema": schema,
        "coverage": coverage,
        "value_diffs": value_diffs,
        "summary": {
            "column_summary": col_summary,
            "matched_rows": matched_count,
            "rows_with_diffs": rows_with_diffs,
            "identical_matched_rows": identical_matched_rows,
            "differing_cells": differing_cells,
            "total_cells": total_cells,
            "overall_match_pct": overall_match_pct,
        },
    }
