import argparse
import errno
import json
import os

import tact.processingScripts.analyzer as analyzer
import tact.processingScripts.datetime_parser as parser
import tact.util.concatCSV
import tact.util.constants as constants
from tact.control.loggingController import \
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

                ret = parser.compile_datetime(
                    f,
                    output_path,
                    config["dateFields"],
                    config["timeField"],
                    config["parsedColumnName"],
                    config["verbose"],
                )
                logger.debug(ret)

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


def update_settings(settings):
    logger.info("Updating settings")
    # write out settings file
    with open(constants.PARSER_CONFIG_FILE_PATH, "w+") as outfile:
        json.dump(settings, outfile)

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
