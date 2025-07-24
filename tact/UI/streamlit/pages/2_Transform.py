import re
import streamlit as st

# placeholder for transform functionality:
# 1. Dataset flipper
# 2. Dataset concat/append w/different columns & regex matching

############################ Main App ############################
st.set_page_config(layout="wide", page_title="TACT: Transform", page_icon=":dolphin:")

api_handle = st.session_state.api_handle

parser_config = api_handle.get_config(config_type="parser")
transform_config = api_handle.get_config(config_type="transform")

st.header("Operations for Transforming a Dataset", divider="rainbow")

input = st.text_input(
    label="Input File Path:", value=parser_config.get("outputFilePath")
)

submit_button = st.button("Submit")

if submit_button:
    if api_handle.update_config(
        config_type="parser", config_to_apply={"inputPath": input}
    ):
        st.success("Config updated.")

data_dict = api_handle.get_data(nrows=10)

# Dataset preview
if data_dict:
    with st.expander(label="Dataset Preview", expanded=True):
        st.table(data=data_dict)

st.markdown(
   body = """
##
Row Enumeration Or Pivoting (flipping)
---
Extract data in the target columns into discrete records (rows) OR
Create new columns from values, and map to another set of values (pivot table)

Data in other columns will remain unchanged. You may also define constant values which will be added to every extracted row.
"""
)
# Allow users to select input columns & constants

mode_options = {
    "enumerate_columns": "Enumerate (flip columns into rows)",
    "pivot_columns": "Pivot (extract values in one column to create new columns)"
}

mode = st.radio(
    "Choose transformation mode:",
    options=list(mode_options.keys()),
    format_func=lambda k: mode_options[k],
    help=":information_source: Please select EITHER enumerate (multi-column) OR pivot (column/value) mode.",
    key="transform_mode"
)


target_data_columns = st.multiselect(
    label="Select target columns:",
    options=list(data_dict.keys()),
    default=list(data_dict.keys()),
    disabled=(mode != "enumerate_columns"),
    key="target_data_columns"
)


col1, col2 = st.columns(2)
with col1:
    pivot_column = st.selectbox(
        label="Column to flip/pivot (values become new columns):",
        options=list(data_dict.keys()),
        disabled=(mode != "pivot_columns")
    )
with col2:
    pivot_value_column = st.selectbox(
        label="Value column (values fill new columns):",
        options=[col for col in data_dict.keys() if col != st.session_state.get("flip_pivot_column_select")],
        disabled=(mode != "pivot_columns")
    )

# We initialize the constants table here so that editing is enabled by default
# Compensating for weird Streamlit behavior
with st.expander(label="Define constants (optional)", expanded=True):
    constants = st.data_editor(
        data=transform_config.get("constants")
        if transform_config.get("constants")
        else {"constant_key": "constant_value"},
        use_container_width=True,
        num_rows="dynamic",
    )

drop_units = st.checkbox(
    label="Drop first row (units)", value=transform_config.get("drop_units")
)

drop_empty_records = st.checkbox(
    label="Drop records with a value of 0 or less in target columns",
    value=transform_config.get("drop_empty_records"),
)

gen_UUID = st.checkbox(
    label="Generate UUID for each record",
    value=transform_config.get("gen_UUID"),
)

split_fields = st.checkbox(
    label="Split input column into multiple columns",
    value=transform_config.get("split_fields"),
    disabled=(mode != "enumerate_columns"),
)

set_occurrence_status = st.checkbox(
    label="Set occurrence status (present/absent) for each record",
    value=transform_config.get("set_occurrence_status"),
    disabled=(mode != "enumerate_columns"),
)

results_column = st.text_input(
    label="Column name for results:", value=transform_config.get("results_column"),
    disabled=(mode != "enumerate_columns"),
)

transform_output_path = st.text_input(
    label="Output path:", value=transform_config.get("transform_output_path")
)

if st.button(label="Flip It!"):
    with st.spinner("Processing..."):
        # Write settings
        outgoing_config = {
            "target_data_columns": target_data_columns,
            "pivot_column": pivot_column,
            "pivot_value_column": pivot_value_column,
            "results_column": results_column,
            "transform_output_path": transform_output_path,
            "drop_units": drop_units,
            "drop_empty_records": drop_empty_records,
            "split_fields": split_fields,
            "set_occurrence_status": set_occurrence_status,
            "gen_UUID": gen_UUID,
            "constants": constants,
        }

        if api_handle.update_config(
            config_type="transform", config_to_apply=outgoing_config
        ):
            st.success(body="Config updated.")
        else:
            st.error(body="Failed to update config.")

        if api_handle.transform(operation=mode):
            st.success("Success - dataset flipped")
            st.balloons()
        else:
            st.error("Failed to flip dataset.")



st.markdown(
    """
    ##
    Row Combination
    ---
    Find records that share 1 - n column values and combine them into a single row. Only one copy of duplicate values will be retained, and unique values will be added under additional columns.
    """
)

# Allow users to select match columns
match_columns = st.multiselect(
    label="Select columns for match:", options=list(data_dict.keys()),
)

append_prefix = st.text_input(label="Prefix for added columns:")

regex_pattern = st.text_input(
    label="Optional: Regex pattern for grouping (applies to match columns)",
    placeholder="e.g. ^[^_]+ for date before first underscore",
    key="combine_rows_regex_pattern"
)
regex_valid = True
regex_error = ""
if regex_pattern:
    try:
        re.compile(regex_pattern)
    except re.error as e:
        regex_valid = False
        regex_error = str(e)
if not regex_valid:
    st.error(f"Invalid regex: {regex_error}")

combine_output_path = st.text_input(
    key="row_combine_output", label="Output path:", placeholder="path/to/output.csv"
)

if st.button(label="Combine Rows!"):
    with st.spinner("Processing..."):
        # Write settings
        outgoing_config = {
            "match_columns": match_columns,
            "append_prefix": append_prefix,
            "combine_output_path": combine_output_path,
        }
        if regex_pattern and regex_valid:
            outgoing_config["match_pattern"] = regex_pattern

        if api_handle.update_config(
            config_type="transform", config_to_apply=outgoing_config
        ):
            st.success(body="Config updated.")
        else:
            st.error(body="Failed to update config.")

        if api_handle.transform(operation="combine_rows"):
            st.success("Success - rows combined.")
        else:
            st.error("Failed to combine rows.")

st.markdown(
    """
    ##
    Conditional Append
    ---
    Append values to all records that match a given criteria. Supports multiple values/conditions.
    """
)
