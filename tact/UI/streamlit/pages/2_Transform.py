import streamlit as st

# placeholder for transform functionality:
# 1. Dataset flipper
# 2. Dataset concat/append w/differnt columns & regex matching

############################ Main App ############################
st.set_page_config(layout="wide", page_title="TACT: Transform", page_icon=":dolphin:")

api_handle = st.session_state.api_handle

parser_config = api_handle.get_config(config_type="parser")
transform_config = api_handle.get_config(config_type="transform")

st.markdown(
    """
#
Operations for Transforming a Dataset
---
"""
)


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
    """
##
Row Enumeration (flipping)
---
Extract data in the target columns into discrete records (rows). Data in other columns will remain unchanged. You may also define constant values which will be added to every extracted row.
"""
)
# Allow users to select input columns & constants
target_data_columns = st.multiselect(
    label="Select target columns:",
    options=list(data_dict.keys()),
    default=list(data_dict.keys()),
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
split_fields = st.checkbox(
    label="Split input column into multiple columns",
    value=transform_config.get("split_fields"),
)
set_occurrence_status = st.checkbox(
    label="Set occurrence status (present/absent) for each record",
    value=transform_config.get("set_occurrence_status"),
)
gen_UUID = st.checkbox(
    label="Generate UUID for each record",
    value=transform_config.get("gen_UUID"),
)

results_column = st.text_input(
    label="Column name for results:", value=transform_config.get("results_column")
)

transform_output_path = st.text_input(
    label="Output path:", value=transform_config.get("transform_output_path")
)

if st.button(label="Flip It!"):
    with st.spinner("Processing..."):
        # Write settings
        outgoing_config = {
            "target_data_columns": target_data_columns,
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

        if api_handle.transform(operation="enumerate_columns"):
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
    label="Select columns for match:", options=parser_config.get("fieldNames")
)
append_prefix = st.text_input(label="Prefix for added columns:")
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
