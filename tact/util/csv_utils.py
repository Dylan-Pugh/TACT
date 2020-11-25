def get_duplicate_columns(input_frame):
    '''
    Get a list of duplicate columns.
    It will iterate over all the columns in dataframe and find the columns whose contents are duplicate.
    :param df: Dataframe object
    :return: List of columns whose contents are duplicates.
    '''

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
            if col.equals(
                    comparison_column) and col.name == comparison_column.name:
                new_columns = input_frame.columns.values
                new_columns[y] = comparison_column.name + "_DUPE"
                input_frame.columns = new_columns

                duplicate_column_indices.add(y)

    return list(duplicate_column_indices)


def drop_duplicate_columns(input_frame, output_encoding):
    # Workaround to allow duplicate columns in Panadas
    input_frame.columns = input_frame.columns.str.split('.').str[0]

    columns_to_drop = get_duplicate_columns(input_frame)

    input_frame.drop(
        input_frame.columns[columns_to_drop],
        axis=1, inplace=True)


def drop_unnamed_columns(input_frame):
    # drop unnamned columns
    input_frame = input_frame.loc[:, ~
                                  input_frame.columns.str.contains('^Unnamed')]


def replace_char_in_headers(input_frame, char_to_replace, replacement_char):
    input_frame.columns = input_frame.columns.str.replace(
        char_to_replace, replacement_char)


def replace_in_rows(input_frame, value_to_replace, replacement_value):
    input_frame.replace(value_to_replace, replacement_value, inplace=True)


def delete_columns(input_frame, columns_to_delete):
    input_frame.drop(columns=columns_to_delete, inplace=True)


def write_out_data_frame(input_frame, output_file, output_encoding):
    input_frame.to_csv(output_file, index=False, encoding=output_encoding)
