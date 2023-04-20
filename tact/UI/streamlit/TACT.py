import streamlit as st

# Custom imports
from settings_sync import write_settings

############################ Main App ############################

st.set_page_config(layout="wide", page_title="TACT: Upload", page_icon=":toolbox:")

# Web App Title & Header
col1, col2 = st.columns([1, 6])

with col1:
    st.image("./front_end/assets/TACT-logos_white.png", use_column_width="auto")

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
    on_change=write_settings(),
)

# This is a workaround because Streamlit doesn't let you get the file path from an uploaded file :(
placeholder = st.empty()

input = placeholder.text_input("Input File Path:")

col1, col2, col3 = st.columns([0.5, 1, 8])
with col1:
    submit_button = st.button("Submit")
with col2:
    test_mode_button = st.button("Test Mode")
with col3:
    st.empty()

if submit_button:
    input = placeholder.text_input("Input File Path:", value=input, key=1)
    st.session_state["inputPath"] = input
    write_settings()
if test_mode_button:
    input = placeholder.text_input(
        "Input File Path:", value="testing/testData/TACT_test.csv", key=2
    )
    st.session_state["inputPath"] = input
    write_settings()

# # Add all your applications (pages) here
# app.add_page("Upload Data", data_upload.app)
# app.add_page("Clean Dataset", data_cleaner.app)
# app.add_page("Run IOOS QC", ioos_qc_runner.app)
# app.add_page("Transform Dataset", data_transform.app)

# #pandas profiling is broken
# #app.add_page("Dataset Report", data_report.app)

# # The main app
# app.run()
