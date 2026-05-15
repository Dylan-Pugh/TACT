import pandas as pd
from tact.control.logging_controller import LoggingController as loggingController

logger = loggingController.get_logger(__name__)

def merge_matched_records(target_df: pd.DataFrame, lookup_df: pd.DataFrame, target_key: str, lookup_key: str, value_columns: list[str]):
    
    try:
        logger.info(f"Merging matched records on {target_key} in target and {lookup_key} in lookup.")

        merged_df = pd.merge(target_df, lookup_df[value_columns], left_on=target_key, right_on=lookup_key, how='left')

    except Exception as e:
        logger.error(
            "Merge FAILED. Something has gone horribly awry!"
            f" Check log for debug information. Error: {e.with_traceback}",
        )
        return None

    logger.info("Merge Successful.")
    return merged_df