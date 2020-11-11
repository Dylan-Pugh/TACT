import datetime

import pandas as pd

from tact.control.logging_controller import \
    LoggingController as loggingController

logger = loggingController.get_logger(__name__)


def pull_date_range(input_file, date_column, date_format, qa_settings_JSON):
    # date_column is parsed_column name from config
    # date_format should also come from constants/config
    logger.info(
        "Pulling %s column from input file: %s",
        date_column,
        input_file)

    dates = pd.read_csv(input_file, usecols=[date_column], squeeze=True)
    try:
        dates = dates.apply(
            lambda current: datetime.datetime.strptime(
                current, date_format))
    except ValueError as ex:
        logger.error(ex.message)

    qa_settings_JSON['minDate'] = datetime.datetime.strftime(
        dates.min(), date_format)
    qa_settings_JSON['maxDate'] = datetime.datetime.strftime(
        dates.max(), date_format)

    return qa_settings_JSON
