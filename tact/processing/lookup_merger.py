import pandas as pd
from tact.control.logging_controller import LoggingController as loggingController

logger = loggingController.get_logger(__name__)

def merge_matched_records(target_df: pd.DataFrame, lookup_df: pd.DataFrame, target_key: str, lookup_key: str, value_columns: list[str]):
    if target_key not in target_df.columns:
        logger.error(f"target_key '{target_key}' not found in target columns: {list(target_df.columns)}")
        return None

    if lookup_key not in lookup_df.columns:
        logger.error(f"lookup_key '{lookup_key}' not found in lookup columns: {list(lookup_df.columns)}")
        return None

    missing_cols = [c for c in value_columns if c not in lookup_df.columns]
    if missing_cols:
        logger.error(f"value_columns not found in lookup: {missing_cols}")
        return None

    try:
        logger.info(f"Merging matched records on {target_key} in target and {lookup_key} in lookup.")

        merged_df = pd.merge(target_df, lookup_df[value_columns], left_on=target_key, right_on=lookup_key, how='left')

    except Exception as e:
        logger.error(
            "Merge FAILED. Something has gone horribly awry! "
            f"Check log for debug information. Error: {e}",
        )
        return None

    logger.info("Merge Successful.")
    return merged_df