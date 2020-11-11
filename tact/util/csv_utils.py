def get_duplicate_columns(input_frame):
    '''
    Get a list of duplicate columns.
    It will iterate over all the columns in dataframe and find the columns whose contents are duplicate.
    :param df: Dataframe object
    :return: List of columns whose contents are duplicates.
    '''

    duplicate_column_names = set()
    # Iterate over all the columns in dataframe
    for x in range(input_frame.shape[1]):
        # Select column at xth index.
        col = input_frame.iloc[:, x]
        # Iterate over all the columns in DataFrame from (x+1)th index till end
        for y in range(x + 1, input_frame.shape[1]):
            # Select column at yth index.
            comparison_column = input_frame.iloc[:, y]
            # Check if two columns at x 7 y index are equal
            if col.equals(
                    comparison_column) and col.name == comparison_column.name:
                duplicate_column_names.add(input_frame.columns.values[y])

    return list(duplicate_column_names)


def drop_duplicate_columns(input_frame, output_encoding):
    input_frame.drop(columns=get_duplicate_columns(input_frame))


def drop_unnamed_columns(input_frame):
    # drop unnamned columns
    input_frame = input_frame.loc[:, ~
                                  input_frame.columns.str.contains('^Unnamed')]


def replace_char_in_headers(input_frame, char_to_replace, replacement_char):
    input_frame.columns = input_frame.columns.str.replace(
        char_to_replace, replacement_char)


def write_out_data_frame(input_frame, output_file, output_encoding):
    input_frame.to_csv(output_file, index=False, encoding=output_encoding)
