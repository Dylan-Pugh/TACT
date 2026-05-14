#!/usr/bin/env python3
"""End-to-end CSV forecasting with TimesFM.

Loads a CSV, runs the system preflight check, loads TimesFM, forecasts
the requested columns, and writes results to a new CSV or JSON.

Usage:
    python forecast_csv.py input.csv --horizon 24
    python forecast_csv.py input.csv --horizon 12 --date-col date --value-cols sales,revenue
    python forecast_csv.py input.csv --horizon 52 --output forecasts.csv
    python forecast_csv.py input.csv --horizon 30 --output forecasts.json --format json

The script automatically:
  1. Runs the system preflight check (exits if it fails).
  2. Loads TimesFM 2.5 from Hugging Face.
  3. Reads the CSV and identifies time series columns.
  4. Forecasts each series with prediction intervals.
  5. Writes results to the specified output file.
"""

from __future__ import annotations
import pandas as pd
import numpy as np
import torch
import timesfm

# TODO: map this to maxHorizon in forecastConfig.json
MAX_HORIZON = 512

_model = None
_model_batch_size = 32


def load_model(batch_size: int = 32):
    """Load and compile the TimesFM model."""
    global _model, _model_batch_size
    
    if _model is not None and _model_batch_size == batch_size:
        return _model

    torch.set_float32_matmul_precision("high")

    print("Loading TimesFM 2.5 from Hugging Face...")
    model = timesfm.TimesFM_2p5_200M_torch.from_pretrained(
        "google/timesfm-2.5-200m-pytorch"
    )

    print(f"Compiling with per_core_batch_size={batch_size}...")
    model.compile(
        timesfm.ForecastConfig(
            max_context=4096,
            max_horizon=MAX_HORIZON,
            normalize_inputs=True,
            use_continuous_quantile_head=True,
            force_flip_invariance=True,
            infer_is_positive=True,
            fix_quantile_crossing=True,
            per_core_batch_size=batch_size,
        )
    )

    _model = model
    _model_batch_size = batch_size
    return model


def forecast_series(
    model, df: pd.DataFrame, value_cols: list[str], horizon: int
) -> dict[str, dict]:
    """Forecast all series and return results dict."""
    inputs = []
    valid_cols = []
    for col in value_cols:
        try:
            values = pd.to_numeric(df[col], errors='coerce').dropna().astype("float32").values
            if len(values) < 10:
                print(f"Column {col} has only {len(values)} valid values, skipping (minimum 10 required)")
                continue
            inputs.append(values)
            valid_cols.append(col)
        except ValueError as e:
            print(f"Column {col} cannot be forecasted: {e}")
            continue

    if not inputs:
        print("No valid time series found for forecasting")
        return {}

    print(f"Forecasting {len(inputs)} series with horizon={horizon}...")
    point, quantiles = model.forecast(horizon=horizon, inputs=inputs)

    results = {}
    for i, col in enumerate(valid_cols):
        results[col] = {
            "forecast": point[i].tolist(),
            "lower_90": quantiles[i, :, 1].tolist(),  # 10th percentile
            "lower_80": quantiles[i, :, 2].tolist(),  # 20th percentile
            "median": quantiles[i, :, 5].tolist(),  # 50th percentile
            "upper_80": quantiles[i, :, 8].tolist(),  # 80th percentile
            "upper_90": quantiles[i, :, 9].tolist(),  # 90th percentile
        }

    return results


def prepare_forecast_df(
    results: dict[str, dict],
    df: pd.DataFrame,
    date_col: str | None,
    horizon: int,
) -> pd.DataFrame:
    """Add forecast results to input data"""
    rows = []
    
    # Pre-compute future dates once (same for all series)
    future_dates = None
    if date_col and date_col in df.columns:
        try:
            df_dates = pd.to_datetime(df[date_col], utc=True, errors='coerce')
            clean_dates = df_dates.dropna().sort_values().drop_duplicates()

            if not clean_dates.empty and len(clean_dates) > 1:
                last_date = clean_dates.iloc[-1]
                
                # Try the strict way first
                freq = pd.infer_freq(clean_dates)
                
                # Fallback: Calculate the statistical mode of the differences
                if freq is None:
                    diffs = clean_dates.diff().dropna()
                    if not diffs.empty:
                        # Use mode for the most common interval
                        mode_freq = diffs.mode()
                        if not mode_freq.empty:
                            freq = mode_freq.iloc[0]
                
                # Generate the range
                if freq:
                    future_dates = pd.date_range(
                        start=last_date, 
                        periods=horizon + 1, 
                        freq=freq
                    )[1:].tolist()
        except Exception:
            pass

    # Default to step numbers if date generation failed
    if future_dates is None:
        future_dates = list(range(1, horizon + 1))

    for col, data in results.items():
        for h in range(horizon):
            row = {
                "series": col,
                "step": h + 1,
                "forecast": data["forecast"][h],
                "lower_90": data["lower_90"][h],
                "lower_80": data["lower_80"][h],
                "median": data["median"][h],
                "upper_80": data["upper_80"][h],
                "upper_90": data["upper_90"][h],
            }
            if isinstance(future_dates[0], (pd.Timestamp,)):
                row[date_col] = future_dates[h]
            rows.append(row)

    return pd.DataFrame(rows)


def forecast_csv(
    input_data: pd.DataFrame,
    horizon: int,
    date_col: str,
    value_cols: list[str],
    ) -> pd.DataFrame:
    
    if value_cols:
        print(f"Forecasting columns: {value_cols}")
    else:
        print("No value columns specified, attempting to auto-detect numeric columns")
    
    # # Clean a copy of the input data: handle MM missing values and parse dates
    # df = input_data.copy()
    # for col in df.columns:
    #     if df[col].dtype == object:
    #         df[col] = pd.to_numeric(df[col], errors='coerce')
    
    model = load_model()

    # here we need to clean up the input data
    results = forecast_series(model, input_data, value_cols, horizon)

    return prepare_forecast_df(results, input_data, date_col, horizon)


def evaluate_forecast(
    input_data: pd.DataFrame,
    date_col: str,
    value_cols: list[str],
) -> tuple[dict, pd.DataFrame]:

    # get total number of records
    # Cut time series in half
    # run forecast on first half -> up to actual end date
    # compare forecast to actual
    # Calculate error/diff metrics
    # Calculate an overall "score" (out of 100)
    # also graph both
    
    total_records = len(input_data)
    if (total_records//2) <= MAX_HORIZON:
        horizon = total_records//2
    else:
        horizon = MAX_HORIZON

    # Grab everything up to the forcast horizon
    context_data = input_data.iloc[:-horizon].copy()

    # Grab the last {horizon} records for comparison
    actual_obs = input_data.iloc[-horizon:].copy()

    # run forecast on first half -> up to actual end date
    forecast_df = forecast_csv(context_data, horizon, date_col, value_cols)
    
    
    # compare forecast to actual
    actual_obs[date_col] = pd.to_datetime(actual_obs[date_col], utc=True)

    metadata = {}
    combined_df = actual_obs.copy()

    for col in value_cols:
        col_forecast = forecast_df[forecast_df["series"] == col][[date_col, "forecast"]].copy()
        col_forecast = col_forecast.dropna(subset=["forecast"])
        col_forecast = col_forecast.rename(columns={"forecast": f"{col}_forecast"})
        
        combined_df = combined_df.merge(col_forecast, on=[date_col], how="left")
        
        # Ensure both columns are numeric before subtraction
        combined_df[col] = pd.to_numeric(combined_df[col], errors='coerce')
        combined_df[f"{col}_forecast"] = pd.to_numeric(combined_df[f"{col}_forecast"], errors='coerce')
        combined_df[f"{col}_error"] = combined_df[f"{col}_forecast"] - combined_df[col]

        diff = combined_df[f"{col}_forecast"].values - combined_df[col].values
        mean_absolute = pd.Series(diff).abs().mean()
        
        metadata[col] = {
            "mean_absolute_percentage_error": float(mean_absolute * 100),
            "forecast_length": int(horizon),
            "forecast_start_date": actual_obs[date_col].iloc[0].strftime('%Y-%m-%d %H:%M:%S'),
            "forecast_end_date": actual_obs[date_col].iloc[-1].strftime('%Y-%m-%d %H:%M:%S'),
            "forecast_timespan": str(actual_obs[date_col].iloc[-1] - actual_obs[date_col].iloc[0]),
            "total_input_records": int(total_records),
            "best_prediction_error": float((combined_df[f"{col}_error"].abs().min()) * 100),
            "worst_prediction_error": float((combined_df[f"{col}_error"].abs().max()) * 100),
            "best_prediction_date": combined_df.loc[combined_df[f"{col}_error"].abs().idxmin(), date_col].strftime('%Y-%m-%d %H:%M:%S'),
            "worst_prediction_date": combined_df.loc[combined_df[f"{col}_error"].abs().idxmax(), date_col].strftime('%Y-%m-%d %H:%M:%S'),
        }

    cleaned_df = combined_df.replace({np.nan: None})

    return metadata, cleaned_df