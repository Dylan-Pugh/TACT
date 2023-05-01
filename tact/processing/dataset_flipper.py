import uuid
import pandas as pd
from tact.control.logging_controller import LoggingController as loggingController

logger = loggingController.get_logger(__name__)


def enumerate_row(
    row,
    field,
    results_column: str,
    split_fields: bool,
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

    # add count of specified species as a new column
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


def process(
    target_data_columns: list,
    results_column: str,
    df: pd.DataFrame,
    drop_units,
    drop_empty_records,
    split_fields: bool,
    set_occurrence_status: bool,
    gen_UUID: bool,
    constants: dict = {},
):
    # select only rows where there is at least one valid (non-zero count) record
    if drop_empty_records:
        valid_records = df.dropna(subset=target_data_columns, how="all")
    else:
        valid_records = df

    # drop units row from records

    if drop_units:
        valid_records = df.iloc[1:, :]

    enumerated_rows = []
    # loop through target column list
    for field in target_data_columns:
        # now enumerate each input row, extracting the values
        for row in valid_records.iterrows():
            # only skip row if value < 0 AND flag is set
            if drop_empty_records and pd.to_numeric(row[1][field]) < 0:
                continue
            else:
                flipped_row = enumerate_row(
                    row,
                    field,
                    results_column,
                    split_fields,
                    set_occurrence_status,
                    gen_UUID,
                    constants,
                )

                # delete other records from flipped row
                for k in target_data_columns:
                    flipped_row.pop(k, None)

                enumerated_rows.append(flipped_row)

    # now convert the list of dicts into a dataframe
    output_frame = pd.DataFrame.from_dict(enumerated_rows)

    return output_frame
