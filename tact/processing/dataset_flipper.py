import re
import uuid
import pandas as pd
from tact.control.logging_controller import LoggingController as loggingController

logger = loggingController.get_logger(__name__)


def enumerate_row(
    row,
    field,
    results_column: str,
    split_fields: bool,
    match_col_variants: bool,
    primary_units: str,
    alt_units: str,
    set_occurrence_status: bool,
    gen_UUID: bool,
    constants,
):
    # expands rows which contain multiple observations into discrete records
    row_data = row[1]
    organism_count = row_data[field]

    # convert to dict so we can mutate
    enumerated_row = row_data.to_dict()

    # determine whether we should derive additional fields from the input column header
    if split_fields:
        split_species = field.rsplit("_", 1)
        scientific_name = split_species[0].replace("_", " ")

        if len(split_species) > 1 and field.rsplit("_", 1)[1]:
            life_stage = field.rsplit("_", 1)[1]

            if life_stage == "N":
                life_stage = "Nauplius"

            enumerated_row["lifeStage"] = (
                life_stage if life_stage != "F" and life_stage != "M" else "adult"
            )

            if life_stage == "F":
                enumerated_row["sex"] = "female"
            elif life_stage == "M":
                enumerated_row["sex"] = "male"
            else:
                enumerated_row["sex"] = "NA"
        else:
            enumerated_row["lifeStage"] = "NA"
            enumerated_row["sex"] = "NA"

        enumerated_row[results_column] = scientific_name
    else:
        enumerated_row[results_column] = field

    #TODO: add handling for multiple unit/value pairs
    # so, if only one unit is specified, then send as arg for organismQuantityType
    # otherwise, we use the unit name as the column name, and assign the organism_count as the value
    # ^^ for each unit/column pair

    if match_col_variants:
        #TODO
        matched_cols = [x for x in enumerated_row.keys() if x != field and field in x]
        if matched_cols:
            for col in matched_cols:
                if col != field:
                    enumerated_row[alt_units] = row_data[col]
                    # pop col out of enumerated row

    # add count of specified species as a new column
    if primary_units:
        enumerated_row[primary_units] = organism_count
    else:
        enumerated_row["organismQuantity"] = organism_count
        # obtained from the metadata
        enumerated_row["organismQuantityType"] = "individuals per m2"

    if set_occurrence_status:
        # this condition should always be True, but leaving check for completeness
        enumerated_row["occurrenceStatus"] = (
            "present"
            if pd.to_numeric(organism_count) > 0 and organism_count != "NaN"
            else "absent"
        )

    if gen_UUID:
        # generate a unique occurrenceID here
        enumerated_row["occurrenceID"] = uuid.uuid4()

    # add constants
    for key, value in constants.items():
        enumerated_row[key] = value

    return enumerated_row

def pivot(
    input_data: pd. DataFrame,
    pivoted_column: str,
    value_column: str
    ) -> pd.DataFrame:
    """
    Simpler than enumerate_rows: takes column, extracts all values in that columns into new columns, and populates
    those columns with the values specified by value_column
    :param input_data: Dataframe being pivoted
    :param pivoted_column: The label for the column which will have its values extracted and turned into other columns
    :param value_column: The values which wil be mapped to the newly created columns
    :return: Pivoted Dataframe (hopefully)
    """

    try:
        pivoted = input_data.pivot(
            index=[col for col in input_data.columns if col not in [pivoted_column, value_column]],
            columns=pivoted_column,
            values=value_column,
        )
    except Exception as e:
        pass

    return pivoted.reset_index()

def process(
    target_data_columns: list,
    results_column: str,
    df: pd.DataFrame,
    drop_units,
    drop_empty_records,
    split_fields: bool,
    match_col_variants: bool,
    primary_units: str,
    alt_units: str,
    set_occurrence_status: bool,
    gen_UUID: bool,
    constants: dict = {},
):
    logger.info(f"Processing columns: {target_data_columns}")

    # select only rows where there is at least one valid (non-zero count) record
    if drop_empty_records:
        valid_records = df.dropna(subset=target_data_columns, how="all")
        logger.debug(f"drop_empty_records: {drop_empty_records}. Dropped empty rows.")
    else:
        valid_records = df

    # drop units row from records

    if drop_units:
        valid_records = df.iloc[1:, :]
        logger.debug(f"drop_units: {drop_units}. Dropped unit row.")

    enumerated_rows = []
    # loop through target column list
    for field in target_data_columns:
        # now enumerate each input row, extracting the values
        for row in valid_records.iterrows():
            # only skip row if flag is set AND value is < 0 or NaN
            try:
                if drop_empty_records and (pd.to_numeric(row[1][field]) <= 0 or pd.isna(row[1][field])):
                    logger.debug(f"drop_empty_records is {drop_empty_records}, and current value: {pd.to_numeric(row[1][field])} < 0.")
                    logger.debug("Skipped row.")
                    continue
            except ValueError as e:
                logger.error(f"Failed to evaluate value as number: {e}")
                logger.error(f"Value: {row[1][field]}")
                continue

            else:
                flipped_row = enumerate_row(
                    row,
                    field,
                    results_column,
                    split_fields,
                    match_col_variants,
                    primary_units,
                    alt_units,
                    set_occurrence_status,
                    gen_UUID,
                    constants,
                )

                # delete other records from flipped row
                # for k in target_data_columns:
                #     flipped_row.pop(k, None)

                # Here we remove all the enumerated columns, as we no longer need them
                flipped_row = {k: v for k,v in flipped_row.items() if k not in target_data_columns}
                
                if match_col_variants:
                    # First find any remaining columns that are super strings of the target (matches)
                    matched_cols = set(key for key in flipped_row if any(target in key for target in target_data_columns))
                    # Then remove those columns as well, as they have also been enumerated
                    flipped_row = {k: v for k,v in flipped_row.items() if k not in matched_cols}

                # More verbose method of achieving the above
                # if match_col_variants:
                #     matched_cols = []
                #     for key in flipped_row.items():
                #         for target in target_data_columns:
                #             if target in key:
                #                 matched_cols.append(key)
                    
                #     flipped_row = {k: v for k,v in flipped_row.items() if k not in matched_cols}

                enumerated_rows.append(flipped_row)

    # now convert the list of dicts into a dataframe
    output_frame = pd.DataFrame.from_dict(enumerated_rows)
    
    return output_frame
