from cProfile import label
import json
import numpy as np
import pandas as pd
import xarray as xr
import streamlit as st
import control.controller as controller
import util.constants as constants
from pandas_profiling import ProfileReport
from streamlit_pandas_profiling import st_profile_report

######################## Helper Functions ########################

def write_settings():
    # syncs the Stremlit session state with TACT settings file
    # session state -> parserConfig.JSON
    #st.write(st.session_state)

    # start with current settings from controller
    config_to_apply = controller.get_settings_json(config_type='parser')

    # update settings from session state, print success message
    config_to_apply["inputPath"] = st.session_state.input_path
    config_to_apply["inputFileEncoding"] = st.session_state.inputFileEncoding
    config_to_apply["outputFilePath"] = st.session_state.outputFilePath
    config_to_apply["parsedColumnName"] = st.session_state.parsedColumnName
    config_to_apply["parsedColumnPosition"] = st.session_state.parsedColumnPosition

    # checks to perform
    config_to_apply["dropDuplicates"] = st.session_state.dropDuplicates

    config_to_apply["fixTimes"] = st.session_state.fixTimes

    config_to_apply["dropEmpty"] = st.session_state.dropEmpty

    config_to_apply["normalizeHeaders"] = st.session_state.normalizeHeaders

    config_to_apply["replaceValues"] = st.session_state.replaceValues

    config_to_apply["deleteColumns"] = st.session_state.deleteColumns

    # write time & date fields as a JSON object
    config_to_apply["dateFields"] = json.loads(st.session_state.dateFields)
    config_to_apply["timeField"] = json.loads(st.session_state.timeField)

    # write replacement args as JSON objects
    config_to_apply["headerValuesToReplace"] = json.loads(st.session_state.headerValuesToReplace)
    config_to_apply["rowValuesToReplace"] = json.loads(st.session_state.rowValuesToReplace)

    config_to_apply["columnsToDelete"] = st.session_state.columnsToDelete.split(',')

    controller.update_settings(config_type='parser', json_to_apply=config_to_apply)

def create_report(df):
    pr = ProfileReport(df, explorative=True)
    st.header('**Input DataFrame**')
    st.write(df)
    st.write('---')
    st.header('**Pandas Profiling Report**')
    st_profile_report(pr)

def display_analysis(config):
    
    with st.form(key='settings_form'):
        #inputs/outputs
        col1, col2 = st.columns([4,1])
        with col1:
            st.text_input(key='inputPath', label='Input file path', value=config["inputPath"])
        with col2:
            st.selectbox(key='inputFileEncoding', label='File Encoding', options=constants.AVAILABLE_ENCODING_MODES)

        st.text_input(key='outputFilePath', label='Output file path', value=config["outputFilePath"])

        #parsed time settings
        col3, col4, col5 = st.columns([1,4,4])
        with col3:
            st.checkbox(key='fixTimes', label='Fix Times', value=config["fixTimes"])
        with col4:
            st.text_input(key='parsedColumnName', label='Parsed Time Column Name', value=config["parsedColumnName"])
            st.text_input(key='dateFields', label='Date Fields',value=json.dumps(config["dateFields"]))
        with col5:
            st.number_input(key='parsedColumnPosition', label='Parsed Column Position', min_value=0, max_value=len(config["fieldNames"]))
            st.text_input(key='timeField', label='Time Fields',value=json.dumps(config["timeField"]))

        #handling for multiple date/time fields

        # Autofills date/time fields into columnsToDelete
        columns_to_delete_args = ""
        for key, value in config["dateFields"].items():
            if config["dateFields"].get(key) != "Not Found":
                if columns_to_delete_args == "":
                    columns_to_delete_args += config["dateFields"].get(key)
                else:
                    columns_to_delete_args += ("," +
                                                config["dateFields"].get(key))
        for key, value in config["timeField"].items():
            if config["timeField"].get(key) != "Not Found":
                if columns_to_delete_args == "":
                    columns_to_delete_args += config["timeField"].get(key)
                else:
                    columns_to_delete_args += ("," +
                                                config["timeField"].get(key))
      
        col6, col7 = st.columns([1,4])
        with col6:
            st.checkbox(key='deleteColumns', label='Delete Selected Columns', value=config["deleteColumns"])
            st.checkbox(key='normalizeHeaders', label='Normalize Headers', value=config["normalizeHeaders"])
            st.checkbox(key='replaceValues', label='Replace Row Values', value=config["replaceValues"])
        with col7:
            st.text_input(key='columnsToDelete', label='Columns To Delete', value=columns_to_delete_args)
            st.text_input(key='headerValuesToReplace', label='Header Values to Replace',value=json.dumps(config["headerValuesToReplace"]))
            st.text_input(key='rowValuesToReplace', label='Row Values to Replace',value=json.dumps(config["rowValuesToReplace"]))


        #Additional fixes
        st.checkbox(key='dropDuplicates', label='Drop Duplicate Rows', value=config["dropDuplicates"])
        st.checkbox(key='dropEmpty', label='Drop Empty Rows', value=config["dropEmpty"])

        st.form_submit_button(label='Update', on_click=write_settings)

def display_preview(preview_JSON):
    #st.write(preview_JSON)
    st.table(preview_JSON)
    return 
       
############################ Main App ############################

st.set_page_config(layout="wide")

# Web App Title & Header
col1, col2 = st.columns([1,6])

with col1:
    st.image('./TACT-logos_white.png', use_column_width='auto')

with col2:
    st.markdown('''
    #
    Welcome to **TACT**, the **T**emporal **A**djustment **C**alculation **T**ool.

    **Credit:** App built in `Python` + `Streamlit` by [Dylan Pugh](https://github.com/Dylan-Pugh) at [GMRI](https://github.com/gulfofmaine).

    ---
    ''')


# Upload CSV data
with st.sidebar.header('1. Upload your data (CSV or NetCDF)'):
    uploaded_file = st.sidebar.file_uploader("Upload your input file", type=["csv","nc",])
    

# This is a workaround because Streamlit doesn't let you get the file path from an uploaded file :(
path_input = st.text_input(key='input_path', label='Input File Path because Streamlit is stupid')
file_path = path_input

# Setting up test mode
if 'test_mode' not in st.session_state:
    st.session_state['test_mode'] = False

if st.button('Press to use Example Dataset') or st.session_state.test_mode:
    uploaded_file = 'testing/testData/TACT_test.csv'
    file_path = 'testing/testData/TACT_test.csv'
    st.session_state.test_mode = True

# Core parser loop
if uploaded_file is not None:
    @st.cache
    def load_file():
        # uploaded_file is already a str in test mode
        file_name = uploaded_file if st.session_state.test_mode else uploaded_file.name

        if file_name.lower().endswith('.csv'):
            csv = pd.read_csv(uploaded_file)
            return csv
        elif file_name.lower().endswith('.nc'):
            datasource = xr.open_dataset(uploaded_file)
            return datasource.to_dataframe()
    df = load_file()

    #create_report(df)
    with st.expander(label='Dataset Preview', expanded=True):
        st.write(df.head())

    with st.expander(label='Parser Settings', expanded=True):
        controller.analyze(file_path)
        config = controller.get_settings_json('parser')
        display_analysis(config)

    with st.expander(label='Preview', expanded=True):
        if st.button(label='Preview Time Changes'):
            # on button press 
            write_settings()
            preview_JSON = controller.generate_preview()
            display_preview(preview_JSON.get("samples"))
    
    with st.expander(label='Process', expanded=True):
        if st.button(label='Process File(s)'):
            write_settings()
            with st.spinner('Processing...'):
                controller.process()
            
            st.success('Processing successful. Output file: ' + st.session_state.outputFilePath)
            st.balloons()
else:
    st.info('Awaiting file upload...')