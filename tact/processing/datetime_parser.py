#! /usr/bin/env python
# -*- coding: iso-8859-1 -*-
import csv
import datetime
import copy
import dateutil
import dateutil.parser
from pytz import timezone
from tact.control.logging_controller import LoggingController as loggingController
import tact.util.record_validator as validator

logger = loggingController.get_logger(__name__)

"""
Simple script to standardize the 'Time' field for AZMP datasets
"""


def create_iso_time(csv_row, date_fields, time_field):
    # Try to parse using the dateutil library, this is the preferred method

    try:
        # Using the Unix epoch as the defualt date - this should never be necessary
        # and is only to assign the correct timezone to the calculated time
        default_date = datetime.datetime(1970, 1, 1, 0, 0, 0)
        default_date = timezone("US/Eastern").localize(default_date)

        date_string = ""

        for current_field in date_fields:
            if date_fields.get(current_field) != "Not Found":
                current_value = date_fields.get(current_field)
                if current_value in csv_row and validator.validate(
                    csv_row[current_value]
                ):
                    if date_string == "":
                        date_string += csv_row[current_value]
                    else:
                        date_string += "/" + csv_row[current_value]

        time_string = ""

        for current_field in time_field:
            if time_field.get(current_field) != "Not Found":
                current_value = time_field.get(current_field)
                if current_value in csv_row and validator.validate(
                    csv_row[current_value]
                ):
                    if time_string == "":
                        time_string += csv_row[current_value]
                    else:
                        time_string += ":" + csv_row[current_value]

        date_time_string = date_string + "T" + time_string

        parsed_datetime = dateutil.parser.parse(date_time_string, default=default_date)

        return parsed_datetime.isoformat()

    except (ValueError, OverflowError) as ex:
        logger.error(str(ex))
        logger.warning("DateUtil parse failed, attempting to manually parse.")

    # Legacy manual/"dirty" parsing - this is error-prone
    # only used if above approach fails

    if len(date_fields) == 1:
        if date_fields.get("date") in csv_row and validator.validate(
            csv_row[date_fields.get("date")]
        ):
            date = csv_row[date_fields.get("date")]
            if len(date) == 8:
                if int(date[4:6]) > 12:
                    # Assumes yyyymmdd format, checks validity of 'month'
                    # if greater than 12, date format is: mmddyyyy
                    [mn, dy, yr] = [date[0:2], date[2:4], date[4:8]]
                else:
                    # Standard yyyymmdd format, just split the String
                    [mn, dy, yr] = [date[4:6], date[6:8], date[0:4]]
            if len(date) == 7:
                # A length of 7 is tricky, grab the first two numbers
                # if they're 19 or 20, we're looking at a year (e.g 1990, 2010)
                if int(date[0:2]) == 19 or int(date[0:2]) == 20:
                    [mn, dy, yr] = [date[4:5], date[5:7], date[0:4]]
                    # Now we add 0 padding to the month, and proceed as normal
                    mn = "0" + mn
                else:
                    # Otherwise, it's likely a mddyyyy format date
                    # in this case, just prepend the 0, and move on
                    date = "0" + date
                    [mn, dy, yr] = [date[0:2], date[2:4], date[4:8]]

            elif len(date) == 6 and date.startswith("7"):
                # Parse datenum from Matlab
                converted_date = datetime.date.fromordinal(
                    int(date) - 366
                ) + datetime.timedelta(days=(int(date) % 1))
                [mn, dy, yr] = [
                    str(converted_date.month),
                    str(converted_date.day),
                    str(converted_date.year),
                ]
        else:
            # choosing Unix epoch if date is null.
            mn = "01"
            dy = "01"
            yr = "1970"

    if len(date_fields) == 3:
        [mn, dy, yr] = [
            csv_row[date_fields.get("month")],
            csv_row[date_fields.get("day")],
            csv_row[date_fields.get("year")],
        ]

    # Splits the 'Time' field into hour and minute, based on positioning.
    # Accounts for time strings of lengths 1 - 4
    if (
        len(time_field) == 1
        and time_field.get("time") in csv_row
        and validator.validate(csv_row[time_field.get("time")])
    ):
        tmp = csv_row[time_field.get("time")]
        sec = "00"

        if len(tmp) == 7:
            tmp = "0" + tmp
        if len(tmp) == 8:
            # Standard hh:mm:ss format, just split the String
            sec = tmp[-2:]
            min = tmp[-5:-3]
            hr = tmp[:-6]
        elif len(tmp) < 3:
            min = tmp
            hr = "00"
        elif len(tmp) >= 3 and len(tmp) <= 5:
            # Here we add the leading zero, if it's missing from 'hour'
            if len(tmp) == 4:
                tmp = "0" + tmp

            min = tmp[-2:]
            hr = tmp[:-3]
        else:
            sec = tmp[-2:]
            min = tmp[-4:-2]
            hr = tmp[:-4]
    elif len(time_field) == 3 and time_field.get("hour") != "Not Found":
        # if input is a well-formed Dict
        [hr, min, sec] = [
            csv_row[time_field.get("hour")],
            csv_row[time_field.get("minute")],
            csv_row[time_field.get("second")],
        ]
    else:
        # choosing mid day, if Date but now NaN Time.
        hr = "12"
        min = "00"
        sec = "00"

    iso_time = "{0}-{1}-{2}T{3}:{4}:{5}-04:00".format(
        yr, mn.zfill(2), dy.zfill(2), hr.zfill(2), min.zfill(2), sec.zfill(2)
    )
    return iso_time


######################################


def compile_datetime(
    f,
    outfile,
    input_date_fields,
    input_time_fields,
    parsed_column_name,
    parsed_column_position,
    verbose=False,
):
    """
    CREATES A reformated OUT_<f>.csv file.
    """

    reader = csv.DictReader(f)
    # NOTE:  fieldnames is just a list, not a dict
    out_flds = copy.deepcopy(reader.fieldnames)

    # get date column names
    date_fields = input_date_fields
    time_field = input_time_fields

    # if verbose: print(in_flds)
    # Output fields begins as a direct cpoy of input fields
    # We then create a new column 'parsed_time' and populate it with the
    # generated ISO date

    if verbose:
        print(out_flds)
    out_flds.insert(parsed_column_position, parsed_column_name)

    writer = csv.DictWriter(open(outfile, "w"), delimiter=",", fieldnames=out_flds)
    writer.writeheader()

    next(reader)
    for csv_row in reader:
        # We discard empty rows here
        if all(value == "" for value in csv_row.values()):
            continue
        orow = csv_row
        this_time = create_iso_time(csv_row, date_fields, time_field)
        orow[parsed_column_name] = this_time

        writer.writerow(orow)

    if verbose:
        print("Created:", outfile)
    return outfile
