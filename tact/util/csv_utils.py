import os
import glob
import re
import pandas as pd


def get_duplicate_columns(input_frame):
    """
    Get a list of duplicate columns.
    Iterate over all the columns in dataframe and find the columns whose contents are duplicate.
    :param df: Dataframe object
    :return: List of columns whose contents are duplicates.
    """

    duplicate_column_indices = set()
    # Iterate over all the columns in dataframe
    for x in range(input_frame.shape[1]):
        # Select column at xth index.
        col = input_frame.iloc[:, x]
        # Iterate over all the columns in DataFrame from (x+1)th index till end
        for y in range(x + 1, input_frame.shape[1]):
            # Select column at yth index.
            comparison_column = input_frame.iloc[:, y]
            # Check if two columns at x & y index are equal
            if col.equals(comparison_column) and col.name == comparison_column.name:
                new_columns = input_frame.columns.values
                new_columns[y] = comparison_column.name + "_DUPE"
                input_frame.columns = new_columns

                duplicate_column_indices.add(y)

    return list(duplicate_column_indices)


def drop_duplicate_columns(input_frame, output_encoding):
    # Workaround to allow duplicate columns in Panadas
    input_frame.columns = input_frame.columns.str.split(".").str[0]

    columns_to_drop = get_duplicate_columns(input_frame)

    input_frame.drop(input_frame.columns[columns_to_drop], axis=1, inplace=True)


def drop_unnamed_columns(input_frame):
    # drop unnamned columns
    # Older, manual method:
    # input_frame = input_frame.loc[:, ~input_frame.columns.str.contains('^Unnamed')]
    input_frame.dropna(inplace=True, axis=1, how="all")


def replace_char_in_headers(input_frame, char_to_replace, replacement_char):
    input_frame.columns = input_frame.columns.str.replace(
        r"\s+|_+", " ", regex=True
    ).str.replace(char_to_replace, replacement_char)


def append_row_header(input_frame: pd.DataFrame, row_index: int = 0, drop_row: bool = False):
    """
    For input DataFrame, take the specified row and append its values to the column names.

    Args:
        input_frame (pd.DataFrame): The DataFrame to modify.
        row_index (int): The index of the row whose values will be appended to the column names. Default is 0 (first row).
    """
    if input_frame.empty or input_frame.shape[0] <= row_index:
        return input_frame

    modified_columns = []
    for current_column in input_frame.columns.drop_duplicates():
        to_process = []

        col_value = input_frame.at[row_index, current_column]
        
        if isinstance(col_value, pd.Series):
            to_process.extend(col_value.values.tolist())
        else:
            to_process.append(col_value)
        
        for new_value in to_process:
            if pd.notnull(new_value) and str(new_value) != '':
                appended_name = f"{current_column}_{str(new_value).strip()}"
                modified_columns.append(appended_name)
            else:
                modified_columns.append(current_column)
  
    input_frame.columns = modified_columns

    if drop_row:
        input_frame.drop(input_frame.index[row_index], inplace=True)
        #input_frame.reset_index(drop=True, inplace=True)


def replace_in_rows(
    input_frame, value_to_replace, replacement_value, target_columns=None
):
    if target_columns is not None and target_columns:
        for current_column in target_columns:
            input_frame[current_column].replace(
                value_to_replace, replacement_value, inplace=True
            )
            input_frame[current_column].fillna(value=replacement_value, inplace=True)
    else:
        input_frame.replace(value_to_replace, replacement_value, inplace=True)
        input_frame.fillna(value=replacement_value, inplace=True)


def delete_columns(input_frame, columns_to_delete):
    input_frame.drop(columns=columns_to_delete, inplace=True)


def write_out_data_frame(input_frame, output_file, output_encoding):
    input_frame.to_csv(output_file, index=False, encoding=output_encoding)


def concat_input_files(input_files, output_encoding, out_path):
    if isinstance(input_files, str):
        # If input is a path to a dir
        os.chdir(input_files)
        extension = "csv"
        all_filenames = [i for i in glob.glob("*.{}".format(extension))]

        # combine all files in the list
        combined_csv = pd.concat([pd.read_csv(f) for f in all_filenames], ignore_index=True)
    else:
        combined_csv = pd.concat(input_files, ignore_index=True)

    combined_csv.drop_duplicates(keep="first", inplace=True)

    # export to csv
    combined_csv.to_csv(out_path, index=False, encoding=output_encoding)
    return out_path


def merge_grouped_rows(group_df, append_prefix):
    source_rows = []
    output_rows = []

    for current_row in group_df.iterrows():
        row_data = current_row[1]
        enumerated_row = row_data.to_dict()

        if source_rows and enumerated_row != source_rows[0]:
            diff_set = set(enumerated_row.items()) - set(source_rows[0].items())
            print(diff_set)

            # retrieve original row and prepare to append
            mutated_row = source_rows[0]

            for current_diff in diff_set:
                mutated_row[append_prefix + current_diff[0]] = current_diff[1]

            output_rows.append(mutated_row)

        elif not source_rows:
            # find and save the first row
            source_rows.append(enumerated_row)
            continue

    return pd.DataFrame.from_dict(output_rows)


def sort_by_time(input_frame: pd.DataFrame, time_fields: list[str] = None) -> pd.DataFrame:

    # create regular expression that matches "Date" and "time" regardless of capitalization
    regex = re.compile(r"(?i)date|time")

    # find first time field that exists in flipped_df or matches the regular expression
    for time_field in time_fields:
        if time_field in input_frame.columns:
            sort_by_column = time_field
            break
        elif regex.search(time_field):
            match = regex.search(time_field).group(0)
            sort_by_column = next(
                (col for col in input_frame.columns if match.lower() in col.lower()),
                None,
            )
            if sort_by_column:
                break
        else:
            # if no time field is found, raise an exception
            raise ValueError("No valid time field found in flipped_df")

    #sort by parsed time and flipped column name, ascending
    input_frame.sort_values(
        by=[
            sort_by_column,
            input_frame.get("results_column"),
        ],
        ascending=True,
        inplace=True,
    )

    return input_frame


def combine_rows(input_frame: pd.DataFrame, match_columns: list, append_prefix="ADDED_", match_pattern: str = None):
    """
    Combines rows in a given dataframe based on provided match criteria.
    The new row will have one copy of all duplicate values, and new columns for each unique value.
    There's probably an 'easier' or more effcient way to do this using a fancy Pandas function, but Pandas is also extremely opaque and I'm too dumb to figure it out.
    I'll buy you a beer if you improve this function.
    :param input_frame: Dataframe object
    :param match_columns: Columns used to determine whether a row 'matches' another
    :param append_prefix: String to append to added column names
    :return: New dataframe with combined rows
    """

    print(f"Match pattern: {match_pattern}")

    if match_pattern:
        # cannot correctly unpack list of cols ,but single col works
        # grouped = input_frame.groupby(by=input_frame[match_columns].apply(lambda x: re.sub(match_pattern, '', str(x))))
        #grouped = input_frame.groupby(by=input_frame['time'].apply(lambda x: re.sub(match_pattern, '', str(x))))
        grouped = input_frame.groupby(by=input_frame[[match_columns]].apply(lambda x: re.sub(match_pattern, '', str(x))))
    else:
        grouped = input_frame.groupby(match_columns)
    
    print("Number of groups:", len(grouped))
    print("Groups:", list(grouped.groups.keys()))
    new_df = grouped.apply(merge_grouped_rows, append_prefix)

    return new_df
