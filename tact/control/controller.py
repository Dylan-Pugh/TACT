import argparse
import errno
import json
import os
import pandas as pd

import tact.processing.analyzer as analyzer
import tact.processing.datetime_parser as parser
import tact.processing.quality_checker as quality_checker
import tact.util.concat_CSV
import tact.util.constants as constants
import tact.util.csv_utils as csv_utils
from tact.control.logging_controller import \
    LoggingController as loggingController

# interacts with GUI, calls analyzer, parser, and quality control
logger = loggingController.get_logger(__name__)


def analyze(input_file):
    # open settings
    with open(constants.PARSER_CONFIG_FILE_PATH) as json_file:
        config = json.load(json_file)

    logger.debug("Analyzing input file: %s", input_file)
    if analyzer.process_file(input_file, config.get("inputFileEncoding")):
        # return path to settings file
        return constants.PARSER_CONFIG_FILE_PATH
    else:
        logger.error("Failed to Create Settings JSON")


def generate_preview(settings):
    return analyzer.create_preview(settings)


def process():
    logger.info("Processing file(s)")

    # open settings
    with open(constants.PARSER_CONFIG_FILE_PATH) as json_file:
        config = json.load(json_file)

        to_process = []
        if config["isDirectory"]:
            # gets list of files, ignoring hidden
            raw_files = [
                f for f in os.listdir(config["inputPath"])
                if not f.startswith(".")
            ]
            # add the full path back in
            to_process = list(
                map(lambda current: config["inputPath"] + "/" + current, raw_files)
            )
            # creates output directory if it does not exist
            if not os.path.exists(os.path.dirname(config["outputFilePath"])):
                try:
                    os.makedirs(os.path.dirname(config["outputFilePath"]))
                except OSError as exc:  # guard against race condition
                    if exc.errno != errno.EEXIST:
                        raise
        else:
            to_process.append(config["inputPath"])

        for current_file in to_process:
            f = open(current_file, encoding=config["inputFileEncoding"])
            if f:
                output_path = config["outputFilePath"]
                if os.path.isdir(
                        config["outputFilePath"]) or config["isDirectory"]:
                    outfile = "OUT_" + os.path.basename(current_file)
                    output_path = output_path + outfile

                # Correct times
                if (config["fixTimes"]):
                    ret = parser.compile_datetime(
                        f,
                        output_path,
                        config["dateFields"],
                        config["timeField"],
                        config["parsedColumnName"],
                        config["parsedColumnPosition"]
                    )
                    logger.debug(ret)

                # Additional fixes:
                if config["dropDuplicates"] or config["dropEmpty"] or config[
                        "normalizeHeaders"] or config["replaceValues"] or config["deleteColumns"]:
                    logger.info(
                        "Additional fixes selected, opening data frame")

                    if os.path.isfile(output_path):
                        input_frame = pd.read_csv(output_path)
                    else:
                        input_frame = pd.read_csv(current_file)

                    if config["dropDuplicates"]:
                        logger.info("Removing duplicate columns")
                        csv_utils.drop_duplicate_columns(
                            input_frame, config["inputFileEncoding"])
                    if config["dropEmpty"]:
                        logger.info("Removing empty columns")
                        csv_utils.drop_unnamed_columns(input_frame)
                    if config["normalizeHeaders"]:
                        logger.info("Replacing characters in column headers")
                        for current_replacement_pair in config["headerValuesToReplace"]:
                            csv_utils.replace_char_in_headers(
                                input_frame, current_replacement_pair.get(
                                    "original"),
                                current_replacement_pair.get("replacement"))
                    if config["replaceValues"]:
                        logger.info("Replacing values in rows")
                        for current_replacement_pair in config["rowValuesToReplace"]:
                            csv_utils.replace_in_rows(
                                input_frame, current_replacement_pair.get(
                                    "original"),
                                current_replacement_pair.get("replacement"))
                    if config["deleteColumns"]:
                        logger.info(
                            "Deleting specified columns: " +
                            ", ".join(config["columnsToDelete"]))
                        if (all(elem in config["fieldNames"]
                                for elem in config["columnsToDelete"])):
                            csv_utils.delete_columns(
                                input_frame, config["columnsToDelete"])
                        else:
                            logger.warning(
                                "Columns specified for deletion do not exist in file, skipping...")

                    # write out file
                    logger.info("Writing out data frame")
                    csv_utils.write_out_data_frame(
                        input_frame, output_path, config["inputFileEncoding"])

    logger.info("Processing complete")


def is_directory(input_path):
    return os.path.isdir(input_path)


def concat_files(input_path):
    # open settings
    with open(constants.PARSER_CONFIG_FILE_PATH) as json_file:
        config = json.load(json_file)

    logger.info("Concatenating files in directory: %s", input_path)
    return tact.util.concatCSV.concat_input_files(
        input_path, config.get("inputFileEncoding"))


def update_settings(settings, path):
    logger.info("Updating settings")
    # write out settings file
    with open(path, "w+") as outfile:
        json.dump(settings, outfile)


def init_quality_check():
    # open settings to pull arguments
    # TODO: how to create and append to JSON file if none exists or is empty

    # open settings
    with open(constants.PARSER_CONFIG_FILE_PATH) as json_file:
        config = json.load(json_file)

    # open QA settings
    with open(constants.QA_CONFIG_PATH) as json_file:
        qa_config = json.load(json_file)

    qa_config = quality_checker.pull_date_range(
        config["outputFilePath"],
        config["parsedColumnName"],
        constants.DEFAULT_PARSED_COLUMN_FORMAT,
        qa_config)

    update_settings(qa_config, constants.QA_CONFIG_PATH)

    ######################################


def run():

    ap = argparse.ArgumentParser()
    ap.add_argument(
        "csv_file", help="CSV filename. Creates OUT_csv_file in current dir.")
    ap.add_argument("encoding", nargs='?',
                    help="encoding with which to open passed file.")
    ap.add_argument("-v", "--verbose", action="store_true",
                    help=" verbose output.")
    args = ap.parse_args()

    # created combined file if input is a directory
    if os.path.isdir(args.csv_file):
        infile = tact.util.concatCSV.concat_input_files(
            args.csv_file, args.encoding)
    elif os.path.isfile(args.csv_file):
        infile = args.csv_file

    f = open(infile, encoding=args.encoding)
    if f:
        process()
        logger.info("Processing...")


if __name__ == "__main__":
    run()
