import json
import streamlit as st
import pandas as pd
import xarray as xr
import control.controller as controller
import front_end.components.dict_table as dt

# placeholder for transform functionality:
# 1. Dataset flipper
# 2. Dataset concat/append w/differnt columns & regex matching

############################ Main App ############################
st.set_page_config(layout="wide", page_title="TACT: Transform", page_icon=":dolphin:")

config = controller.get_settings_json("parser")

st.markdown(
    """
#
Operations for Transforming a Dataset
---
"""
)

df = controller.get_df_from_path(config_type="parser")

with st.expander(label="Current format", expanded=True):
    st.write(df.head())

st.markdown(
    """
##
Row Enumeration (flipping)
---
Extract data in the target columns into discrete records (rows). Data in other columns will remain unchanged. You may also define constant values which will be added to every extracted row.
"""
)
# Allow users to select input columns & constants
target_columns = st.multiselect(
    label="Select target columns:", options=df.columns, default=df.columns.to_list()
)

col1, col2 = st.columns([1, 6])

with col1:
    append_constants = st.checkbox(label="Append Constants")
with col2:
    constants = st.text_input(
        label="Define constants as key/value pairs:",
        value={"key1": "value1", "key2": "value2", "key3": 0},
    )


drop_units = st.checkbox(label="Drop first row (units)")
drop_empty_records = st.checkbox(
    label="Drop records with a value of 0 or less in target columns"
)
split_fields = st.checkbox(label="Split input column into multiple columns")

results_column = st.text_input(label="Column name for results:", value="scientificName")

output_path = st.text_input(label="Output path:", value=config["outputFilePath"])

# testing
# target_columns = ['7/23/2020_cells/Liter',
#                         '8/12/2020_cells/Liter',
#                         '8/19/2020_cells/Liter',
#                         '9/10/2020_cells/Liter']

# target_columns = ['7/23/2020_cells/Liter',
#                     '7/23/2020_ng C/ Liter',
#                     '8/12/2020_cells/Liter',
#                     '8/12/2020_ng C/ Liter',
#                     '8/19/2020_cells/Liter',
#                     '8/19/2020_ng C/ Liter',
#                     '9/10/2020_cells/Liter',
#                     '9/10/2020_ng C/ Liter']

# constants = {"latitude": 42.8646, "longitude": -69.8632, "Station": "WBTS", "depth": 20}

# constants_table = dt.DictTable(json.loads(constants), "Constants:")

# constants_table.render()

if st.button(label="Flip It!"):
    with st.spinner("Processing..."):
        if append_constants:
            controller.flip_dataset(
                target_columns,
                results_column,
                output_path,
                drop_units,
                drop_empty_records,
                split_fields,
                constants,
            )
        else:
            controller.flip_dataset(
                target_columns,
                results_column,
                output_path,
                drop_units,
                drop_empty_records,
                split_fields,
            )
    st.success("Success - dataset flipped")

st.markdown(
    """
    ##
    Row Combination
    ---
    Find records that share 1 - n column values and combine them into a single row. Only one copy of duplicate values will be retained, and unique values will be added under additional columns.
    """
)

# Allow users to select match columns
match_columns = st.multiselect(label="Select columns for match:", options=df.columns)
append_prefix = st.text_input(label="Prefix for added columns:")
combine_output_path = st.text_input(
    key="row_combine_output", label="Output path:", placeholder="path/to/output.csv"
)

if st.button(label="Combine Rows!"):
    with st.spinner("Processing..."):
        controller.combine_rows(match_columns, combine_output_path, append_prefix)
    st.success("Success - rows combined")

st.markdown(
    """
    ##
    Conditional Append
    ---
    Append values to all records that match a given criteria. Supports multiple values/conditions.
    """
)
