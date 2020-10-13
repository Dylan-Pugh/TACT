import datetime

import pandas as pd

from tact.control.loggingController import \
    LoggingController as loggingController

logger = loggingController.get_logger(__name__)


def pull_date_range(input_file, date_column, date_format, report_JSON):
    logger.info(
        "Pulling %s column from input file: %s",
        date_column,
        input_file)

    dates = pd.read_csv(input_file, usecols=[date_column], squeeze=True)
    dates = dates.apply(
        lambda current: datetime.datetime.strptime(
            current, date_format))

    report_JSON['minDate'] = dates.min()
    report_JSON['maxDate'] = dates.max()

    return report_JSON
