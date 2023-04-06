import pandas as pd
from control.logging_controller import \
    LoggingController as loggingController

logger = loggingController.get_logger(__name__)

def enumerate_row(row, field, constants):
    # expands rows which contain multiple observations into discrete records
    row_data = row[1]
    organism_count = row_data[field]

    # convert to dict so we can mutate
    enumerated_row = row_data.to_dict()

    split_field = field.rsplit('_', 1)
    time = split_field[0].replace('_', ' ')
    units = split_field[1]

    enumerated_row['time'] = time
    
    # add count of specified species as a new column
    enumerated_row['organismQuantity'] = organism_count
    # obtained from the metadata
    enumerated_row['organismQuantityType'] = units

    # add constants
    for key, value in constants.items():
        enumerated_row[key] = value

    return enumerated_row

def process(target_data_columns: list, df: pd.DataFrame, drop_units, drop_empty_records, constants: dict={}):
   
    # select only rows where there is at least one valid (non-zero count) record
    if drop_empty_records:
        valid_records = df.loc[(pd.notna(df[target_data_columns])).all(1)]
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
                flipped_row = enumerate_row(row, field, constants)

                # delete other records from flipped row
                for k in target_data_columns:
                    flipped_row.pop(k, None)

                enumerated_rows.append(flipped_row)

    
    # now convert the list of dicts into a dataframe
    output_frame = pd.DataFrame.from_dict(enumerated_rows)

    # sort by time, ascending
    output_frame.sort_values(by='time', ascending=True, inplace=True)
    return output_frame