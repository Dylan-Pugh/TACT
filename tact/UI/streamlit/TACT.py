import os
import streamlit as st
from utils.api_handler import ApiHandler


############################ Main App ############################

st.set_page_config(layout="wide", page_title="TACT: Upload", page_icon=":toolbox:")

# Get our API handler
if "api_handle" not in st.session_state:
    st.session_state["api_handle"] = ApiHandler(base_url=os.getenv("API_URL"))

api_handle = st.session_state.api_handle

# Web App Title & Header
col1, col2 = st.columns([1, 6])

with col1:
    st.image(
        "tact/UI/streamlit/assets/TACT-logos_white.png",
        use_column_width="auto",
    )

with col2:
    st.markdown(
        """
    #
    Welcome to **TACT**, the **T**emporal **A**djustment **C**alculation **T**ool.

    **Credit:** App built in `Python` + `Streamlit` by [Dylan Pugh](https://github.com/Dylan-Pugh) at [GMRI](https://github.com/gulfofmaine).

    ---
    """
    )

st.sidebar.success("Select tool above.")

# Upload CSV data
input_file = st.file_uploader(
    "Upload your input file",
    type=[
        "csv",
        "nc",
    ],
    accept_multiple_files=True,
)

# This is a workaround because Streamlit doesn't let you get the file path from an uploaded file :(
placeholder = st.empty()

file_path_from_settings = api_handle.get_config(config_type="parser", field="inputPath")

input = placeholder.text_input(label="Input File Path:", value=file_path_from_settings)

col1, col2, col3 = st.columns([1, 1, 8])

with col1:
    submit_button = st.button("Submit")
with col2:
    test_mode_button = st.button("Test Mode")
with col3:
    st.empty()

if submit_button:
    if api_handle.update_config(
        config_type="parser", config_to_apply={"inputPath": input}
    ):
        st.success("Config updated.")

if test_mode_button:
    input = placeholder.text_input(
        "Input File Path:", value="testing/testData/TACT_test.csv", key=2
    )
    st.write("Path is: ", input)
    if api_handle.update_config(
        config_type="parser", config_to_apply={"inputPath": input}
    ):
        st.success("Config updated.")
