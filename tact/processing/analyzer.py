import csv
import json
import os
import re

import tact.processing.datetime_parser as datetime_parser
import tact.util.constants as constants
from tact.control.logging_controller import LoggingController as loggingController

logger = loggingController.get_logger(__name__)


def compile_settings_file(input_string):
    settings_JSON = {}
    settings_JSON["inputPath"] = input_string
    settings_JSON["pathForPreview"] = input_string
    settings_JSON["isDirectory"] = False
    settings_JSON["concatFiles"] = False
    settings_JSON["inputFileEncoding"] = constants.DEFAULT_ENCODING
    settings_JSON["parsedColumnName"] = constants.DEFAULT_PARSED_COLUMN_NAME
    settings_JSON["parsedColumnPosition"] = constants.DEFAULT_PARSED_COLUMN_POSITION
    settings_JSON["dropDuplicates"] = True
    settings_JSON["fixTimes"] = True
    settings_JSON["dropEmpty"] = True
    settings_JSON["normalizeHeaders"] = True
    settings_JSON["replaceValues"] = True
    settings_JSON["deleteColumns"] = True
    settings_JSON["headerValuesToReplace"] = constants.DEFAULT_HEADER_REPLACEMENTS
    settings_JSON["rowValuesToReplace"] = constants.DEFAULT_ROW_VALUE_REPLACEMENTS
    settings_JSON["columnsToDelete"] = ["VALUES", "TO", "DELETE"]

    # For testing
    settings_JSON["dropDuplicates"] = True

    outfile = "/OUT_" + os.path.basename(input_string)
    settings_JSON["outputFilePath"] = os.path.dirname(input_string) + outfile

    if os.path.isdir(input_string):
        settings_JSON["isDirectory"] = True
        settings_JSON["outputFilePath"] = input_string + "/combined.csv"

    return settings_JSON


def find_date_components(field_names, settings_file):
    mn = dy = yr = "Not Found"

    date_search_pattern = re.compile("^date.*", re.IGNORECASE)
    month_search_pattern = re.compile("month|mnth(?=s| |$)", re.IGNORECASE)
    day_search_pattern = re.compile("day(?=s| |$)", re.IGNORECASE)
    year_search_pattern = re.compile("year(?=s| |$)", re.IGNORECASE)

    for current in field_names:
        date_match = date_search_pattern.match(current)
        if date_match:
            settings_file["dateFields"] = {"date": date_match.group(0)}
            return settings_file

        month_match = month_search_pattern.match(current)
        if month_match:
            mn = month_match.group(0)
            continue

        day_match = day_search_pattern.match(current)
        if day_match:
            dy = day_match.group(0)
            continue

        year_match = year_search_pattern.match(current)
        if year_match:
            yr = year_match.group(0)
            continue

    settings_file["dateFields"] = {"year": yr, "month": mn, "day": dy}
    return settings_file


def find_time_field(field_names, settings_file):
    hr = min = sec = "Not Found"

    time_search_pattern = re.compile("^time.*", re.IGNORECASE)
    hour_search_pattern = re.compile("^h(?=our|r)", re.IGNORECASE)
    minute_search_pattern = re.compile("^min(?=ute|s|$)", re.IGNORECASE)
    second_search_pattern = re.compile("sec(?=ond|s|$)", re.IGNORECASE)

    for current in field_names:
        time_match = time_search_pattern.match(current)
        if time_match:
            settings_file["timeField"] = {"time": time_match.group(0)}
            return settings_file

        hour_match = hour_search_pattern.match(current)
        if hour_match:
            hr = hour_match.string
            continue

        mintute_match = minute_search_pattern.match(current)
        if mintute_match:
            min = mintute_match.string
            continue

        second_match = second_search_pattern.match(current)
        if second_match:
            sec = second_match.string
            continue

    settings_file["timeField"] = {"hour": hr, "minute": min, "second": sec}
    return settings_file


def process_file(input_path, input_encoding):
    # compile basic settings
    # logger.info("Compiling settings")
    # settings_JSON = compile_settings_file(input_path)

    with open(constants.PARSER_CONFIG_FILE_PATH) as json_file:
        config = json.load(json_file)

    # if isDirectory, get path to first file in dir, and proceed
    if config["isDirectory"]:
        # remove trailing slash
        if config["inputPath"].endswith("/"):
            config["inputPath"] = config["inputPath"].removesuffix("/")

        # gets list of files, ignoring hidden
        raw_files = [
            f for f in os.listdir(config["inputPath"]) if not f.startswith(".")
        ]
        # add the full path back in
        file_paths = list(
            map(lambda current: config["inputPath"] + "/" + current, raw_files)
        )

        input_path = file_paths[0]

        config["pathForPreview"] = input_path

        logger.info(
            "Input path is a directory, retrieving first file for preview: %s",
            input_path,
        )

    f = open(input_path, encoding=input_encoding)
    logger.debug("Opened file: %s", input_path)

    # # optionally skipping header rows
    # if settings_JSON['headerRow']:
    #     for i in range(settings_JSON['headerRow'] - 1):
    #         f.next()

    reader = csv.DictReader(f)
    # get field names and update
    field_names = reader.fieldnames
    config["fieldNames"] = field_names

    # get date & time fields
    find_date_components(field_names, config)
    find_time_field(field_names, config)

    # write out settings file
    with open(constants.CONFIG_FILE_PATHS["parser"], "w") as outfile:
        json.dump(config, outfile)
        logger.info("Settings written to: %s", constants.CONFIG_FILE_PATHS["parser"])

    return True


# open file
# grab a subset of rows
# grab one row for each unique date or time format
# get the length of all records
# call create_iso_time(csv_row, dateFields, timeField)
# output the results to a JSON file and return
def create_preview(config):
    logger.info("Generating preview")

    # parse preview file file
    with open(config["pathForPreview"], encoding=config["inputFileEncoding"]) as f:
        reader = csv.DictReader(f)

        # skipping n rows to get to data
        next(reader)

        sample_JSON = {}
        sample_JSON["samples"] = []
        known_date_lengths = []
        known_time_lengths = []
        # TODO: add handling for multiple date fields
        # TODO: add option to start processing at arbitary line (in case data doesn't start on line #2)
        # take sum of characters in all date fields
        for csv_row in reader:
            # set lengths
            date_length = 0
            time_length = 0

            if config["dateFields"] != "Not Found":
                for field in config["dateFields"]:
                    if config["dateFields"][field] != "Not Found":
                        date_length += len(csv_row[config["dateFields"][field]])

            if config["timeField"] != "Not Found":
                for field in config["timeField"]:
                    if config["timeField"][field] != "Not Found":
                        time_length += len(csv_row[config["timeField"][field]])

            if (
                date_length not in known_date_lengths
                or time_length not in known_time_lengths
            ):
                current = {}
                # construct new JSON date object by looping through the fields in
                # config['dateFields']
                for key, value in config["dateFields"].items():
                    if value != "Not Found":
                        field_name = "Original_" + value
                        current[field_name] = csv_row[config["dateFields"].get(key)]

                for key, value in config["timeField"].items():
                    if value != "Not Found":
                        field_name = "Original_" + value
                        current[field_name] = csv_row[config["timeField"].get(key)]

                current["Transformation"] = datetime_parser.create_iso_time(
                    csv_row, config["dateFields"], config["timeField"]
                )
                sample_JSON["samples"].append(current)

                # add relevant field length to known values
                if date_length not in known_date_lengths:
                    known_date_lengths.append(date_length)

                if time_length not in known_time_lengths:
                    known_time_lengths.append(time_length)

    return sample_JSON
