import argparse
import errno
import json
import os
import re
import pandas as pd
from typing import Any, Dict, Union

import tact.processing.analyzer as analyzer
import tact.processing.dataset_flipper as flipper
import tact.processing.datetime_parser as parser
import tact.processing.quality_checker as quality_checker
import tact.processing.xml_generator as xml_generator
import tact.processing.taxonomic_name_matcher as taxa_matcher
import tact.util.constants as constants
import tact.util.csv_utils as csv_utils
from tact.control.logging_controller import LoggingController as loggingController

# interacts with API, calls analyzer, parser, and quality control
logger = loggingController.get_logger(__name__)


def get_settings_json(config_type):
    logger.debug(f"Fetching target config: {config_type}")

    try:
        # open settings
        with open(constants.CONFIG_FILE_PATHS[config_type]) as json_file:
            logger.debug(f"File found: {constants.CONFIG_FILE_PATHS[config_type]}")
            return json.load(json_file)
    except (KeyError, FileNotFoundError) as ex:
        logger.error(str(ex))
        logger.error(f"{config_type} config file not found.")


def update_settings(config_type: str, json_to_apply: Dict[str, Any]) -> bool:
    logger.info("Updating settings")
    try:
        # open settings
        with open(constants.CONFIG_FILE_PATHS[config_type], "r") as infile:
            logger.debug(f"File found: {constants.CONFIG_FILE_PATHS[config_type]}")

            data = json.load(infile)

        # update settings with new data
        for key, value in json_to_apply.items():
            data[key] = value
            logger.debug(f"Updated key: {key} with value: {value}.")

        # write out updated settings file
        with open(constants.CONFIG_FILE_PATHS[config_type], "w") as outfile:
            json.dump(data, outfile, indent=6)

        return True
    except (KeyError, FileNotFoundError) as ex:
        logger.error(str(ex))
        logger.error(f"Config file: {config_type} not found.")
        return False


def analyze():
    # open settings
    with open(constants.PARSER_CONFIG_FILE_PATH) as json_file:
        config = json.load(json_file)

    input_path = config.get("inputPath")
    inputFileEncoding = config.get("inputFileEncoding")

    logger.debug(f"Analyzing input file: {input_path}")
    if analyzer.process_file(input_path=input_path, input_encoding=inputFileEncoding):
        # return path to settings file
        return constants.PARSER_CONFIG_FILE_PATH
    else:
        logger.error("Failed to Create Settings JSON")


def generate_preview():
    # open settings
    with open(constants.PARSER_CONFIG_FILE_PATH) as json_file:
        config = json.load(json_file)
        return analyzer.create_preview(config)


def get_data(kwargs: Dict = {}) -> Union[pd.DataFrame, str, Dict]:
    """Loads the currently active file and returns it in the requested format, defaults to Dict.

    Args:
        kwargs (Dict), including:
            format (str): Format to return the data in. Options: "dataframe", "json", "dict".
            nrows (int): Number of rows to read.

    Returns:
        Union[pd.DataFrame, str, Dict]: Data in the requested format.
    """
    # parse kwargs
    format = None

    # we want to remove format, so the rest of the kwargs can be passed to pd.read_csv
    if "format" in kwargs:
        format = kwargs.pop("format")
    if "nrows" in kwargs:
        try:
            kwargs["nrows"] = int(kwargs["nrows"])
        except ValueError as e:
            logger.error(f"Error parsing nrows arg: {e}")
    
    # Default to parser if not provided
    request_type = kwargs.pop("request_type", "parser")
    try:
        with open(constants.CONFIG_FILE_PATHS[request_type]) as json_file:
            config = json.load(json_file)
            if request_type == "parser":
                file_path = config.get("inputPath")
            elif request_type == "transform":
                file_path = config.get("transform_output_path")
    except ValueError as e:
        logger.error(
            f"Unknown request type: {request_type}: {e}"
        )



    if is_directory(file_path):
        logger.info(f"Input path is directory: {file_path}")
        logger.info("Found files: ")
        logger.info(os.listdir(file_path))
        return
    else:
        if file_path.lower().endswith(".csv"):
            try:
                df = pd.read_csv(filepath_or_buffer=file_path, **kwargs)

                if format == "dataframe":
                    return df
                if format == "json":
                    return df.to_json()
                else:
                    return df.to_dict()

            except FileNotFoundError as e:
                logger.error(f"Target dataset does not exist: {e}")
            except ValueError as e:
                logger.error(
                    f"Dataset could not be converted to requested type: {format}: {e}"
                )

        elif file_path.lower().endswith(".nc"):
            # datasource = xr.open_dataset(file_path)
            # return datasource.to_dataframe()
            raise NotImplementedError


def process():
    logger.info("Processing file(s)")

    # open settings
    with open(constants.PARSER_CONFIG_FILE_PATH) as json_file:
        config = json.load(json_file)

        to_process = []
        if config["isDirectory"]:
            # gets list of files, ignoring hidden
            raw_files = [
                f for f in os.listdir(config["inputPath"]) if not f.startswith(".")
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
                if os.path.isdir(config["outputFilePath"]) or config["isDirectory"]:
                    outfile = "OUT_" + os.path.basename(current_file)
                    output_path = output_path + outfile

                # Correct times
                if config["fixTimes"]:
                    ret = parser.compile_datetime(
                        f,
                        output_path,
                        config["dateFields"],
                        config["timeField"],
                        config["parsedColumnName"],
                        config["parsedColumnPosition"],
                    )
                    logger.debug(ret)

                # Additional fixes:
                if (
                    config["dropDuplicates"]
                    or config["dropEmpty"]
                    or config["normalizeHeaders"]
                    or config["replaceValues"]
                    or config["deleteColumns"]
                ):
                    logger.info("Additional fixes selected, opening data frame")

                    if os.path.isfile(output_path):
                        input_frame = pd.read_csv(output_path)
                    else:
                        input_frame = pd.read_csv(current_file)

                    if config["dropDuplicates"]:
                        logger.info("Removing duplicate columns")
                        csv_utils.drop_duplicate_columns(
                            input_frame, config["inputFileEncoding"]
                        )
                    if config["dropEmpty"]:
                        logger.info("Removing empty columns")
                        csv_utils.drop_unnamed_columns(input_frame)
                    if config["deleteColumns"]:
                        logger.info(
                            "Deleting specified columns: "
                            + ", ".join(config["columnsToDelete"])
                        )
                        if all(
                            elem in config["fieldNames"]
                            for elem in config["columnsToDelete"]
                        ):
                            csv_utils.delete_columns(
                                input_frame, config["columnsToDelete"]
                            )
                        else:
                            logger.warning(
                                "Columns specified for deletion do not exist in file, skipping..."
                            )
                    if config["normalizeHeaders"]:
                        logger.info("Replacing characters in column headers")
                        for current_replacement_pair in config["headerValuesToReplace"]:
                            csv_utils.replace_char_in_headers(
                                input_frame,
                                current_replacement_pair.get("original"),
                                current_replacement_pair.get("replacement"),
                            )
                    if config["replaceValues"]:
                        logger.info("Replacing values in rows")
                        for current_replacement_pair in config["rowValuesToReplace"]:
                            csv_utils.replace_in_rows(
                                input_frame,
                                current_replacement_pair.get("original"),
                                current_replacement_pair.get("replacement"),
                                config.get("columnsForReplace"),
                            )

                    # write out file
                    logger.info("Writing out data frame")
                    csv_utils.write_out_data_frame(
                        input_frame, output_path, config["inputFileEncoding"]
                    )

    logger.info("Processing complete")
    return True


def is_directory(input_path):
    return os.path.isdir(input_path)


def concat_files(input_path):
    # open settings
    with open(constants.PARSER_CONFIG_FILE_PATH) as json_file:
        config = json.load(json_file)

    logger.info("Concatenating files in directory: %s", input_path)
    return csv_utils.concat_input_files(input_path, config.get("inputFileEncoding"))


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
        qa_config,
    )

    update_settings(qa_config, constants.QA_CONFIG_PATH)

    ######################################


def get_xml_params(edd_type):
    logger.info("EDDType selected, updating settings")
    with open(constants.XML_LIB_PATH) as json_file:
        xml_lib = json.load(json_file)

    with open(constants.XML_CONFIG_PATH) as json_file:
        xml_config = json.load(json_file)

    if edd_type in xml_lib and edd_type in xml_lib["EDDTypes"]:
        xml_config["eddType"] = edd_type
        xml_config["parameters"] = xml_lib[edd_type].get("parameters")

    update_settings(xml_config, constants.XML_CONFIG_PATH)


def generate_xml():
    xml_generator.invoke(constants.XML_CONFIG_PATH)


def flip_dataset():
    transform_config = get_settings_json("transform")

    logger.info("Flipping dataset...")
    logger.debug(
        "Flipper args: target columns: {}".format(
            transform_config.get("target_data_columns")
        )
    )
    logger.debug(
        "Flipper args: constants: {}".format(transform_config.get("constants"))
    )
    logger.debug(
        "Flipper args: transform_output_path: {}".format(
            transform_config.get("transform_output_path")
        )
    )

    df = get_data(kwargs={"format": "dataframe"})

    # if constants:
    #     constants = json.loads(constants)

    flipped_df = flipper.process(
        transform_config.get("target_data_columns"),
        transform_config.get("results_column"),
        df,
        transform_config.get("drop_units"),
        transform_config.get("drop_empty_records"),
        transform_config.get("split_fields"),
        transform_config.get("set_occurrence_status"),
        transform_config.get("gen_UUID"),
        transform_config.get("constants"),
    )

    parser_config = get_settings_json("parser")

    # create list of possible time fields
    time_fields = [
        parser_config.get("parsedColumnName"),
        parser_config.get("timeField").get("time"),
    ]

    # create regular expression that matches "Date" and "time" regardless of capitalization
    regex = re.compile(r"(?i)date|time")

    # find first time field that exists in flipped_df or matches the regular expression
    for time_field in time_fields:
        if time_field in flipped_df.columns:
            sort_by_column = time_field
            break
        elif regex.search(time_field):
            match = regex.search(time_field).group(0)
            sort_by_column = next(
                (col for col in flipped_df.columns if match.lower() in col.lower()),
                None,
            )
            if sort_by_column:
                break
    else:
        # if no time field is found, raise an exception
        raise ValueError("No valid time field found in flipped_df")

    # sort by parsed time and flipped column name, ascending
    flipped_df.sort_values(
        by=[
            sort_by_column,
            transform_config.get("results_column"),
        ],
        ascending=True,
        inplace=True,
    )

    csv_utils.write_out_data_frame(
        flipped_df,
        transform_config.get("transform_output_path"),
        parser_config["inputFileEncoding"],
    )

    return True


def combine_rows():
    transform_config = get_settings_json("transform")

    logger.info("Combining rows...")

    df = get_data(kwargs={"format": "df"})

    results_df = csv_utils.combine_rows(
        df,
        transform_config.get("columns_to_match"),
        transform_config.get("append_prefix"),
    )

    logger.info(
        "Row combination successful, writing out file: {}".format(
            transform_config.get("combine_output_path")
        )
    )

    parser_config = get_settings_json("parser")

    csv_utils.write_out_data_frame(
        results_df,
        transform_config.get("combine_output_path"),
        parser_config["inputFileEncoding"],
    )


def prepare_worms_lookup() -> pd.DataFrame:
    transform_config = get_settings_json("transform")

    input_frame = get_data(kwargs={"format": "dataframe"})
    target_column = transform_config.get("target_column_for_taxon")

    worms_lut = taxa_matcher.gen_worms_lookup(occurrence=input_frame, target_column=target_column)

    csv_utils.write_out_data_frame(
        input_frame=worms_lut,
        output_file=constants.WORMS_LOOKUP_PATH,
        output_encoding="utf-8-sig",
        )
    
    return worms_lut
    

def validate_taxonomic_names():
    transform_config = get_settings_json("transform")
    parser_config = get_settings_json("parser")

    target_column = transform_config.get("target_column_for_taxon")
    accepted_values = transform_config.get("accepted_taxon_matches")
    output_path = transform_config.get("transform_output_path")
    output_encoding = parser_config.get("inputFileEncoding")

    input_frame = get_data(kwargs={"format": "dataframe"})

    try:
        lut_worms = pd.read_csv(constants.WORMS_LOOKUP_PATH)

        merged_data = taxa_matcher.merge_matched_taxa(
            input_df=input_frame,
            taxa_info=lut_worms,
            target_values=accepted_values,
            target_column=target_column
            
        )

        #input_frame = pd.merge(input_frame, lut_worms, how="left", on=target_column)

        csv_utils.write_out_data_frame(merged_data, output_path, output_encoding)

        return True
    except Exception as e:
        logger.error(f"Failed to validate taxonomic names: {e}")
        return False


def generate_taxonomic_preview() -> Dict:
    transform_config = get_settings_json("transform")
    target_column = transform_config.get("target_column_for_taxon")

    lut_worms = prepare_worms_lookup()

    # open file, maybe only fetch a subset of rows ~10?
    input_frame = get_data(kwargs={"format": "dataframe"})

    return taxa_matcher.preview_changes(input_df=input_frame, worms_lut=lut_worms, target_column=target_column)


def run():
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "csv_file", help="CSV filename. Creates OUT_csv_file in current dir."
    )
    ap.add_argument(
        "encoding", nargs="?", help="encoding with which to open passed file."
    )
    ap.add_argument("-v", "--verbose", action="store_true", help=" verbose output.")
    args = ap.parse_args()

    # created combined file if input is a directory
    if os.path.isdir(args.csv_file):
        infile = csv_utils.concat_input_files(args.csv_file, args.encoding)
    elif os.path.isfile(args.csv_file):
        infile = args.csv_file

    f = open(infile, encoding=args.encoding)
    if f:
        process()
        logger.info("Processing...")


if __name__ == "__main__":
    run()
