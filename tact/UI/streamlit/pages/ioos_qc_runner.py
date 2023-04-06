from cProfile import label
import streamlit as st
import pandas as pd
import json
import control.controller as controller
from processing.qartod_handler import QARTODHandler

config_file_path = "qc_config.json"

def write_config(config_to_write):
    with open (config_file_path, 'w') as out_file:
        json.dump(config_to_write, out_file)

@st.cache
def convert_df(df):
    return df.to_csv().encode('utf-8')

def display_qc_results(input_results):
    st.write(input_results)
    
def app():
    complete_flag = False
    # Load QC config
    ioos_qc_config = controller.get_settings_json("IOOS_QC_CONFIG_PATH")
    tact_settings = controller.get_settings_json("parser")

    df = pd.read_csv(tact_settings['inputPath'])

    col1, col2 = col1, col2 = st.columns([1,1])
    with col1:
        selected_column = st.selectbox(label='Select Input Variable', options=df.columns)
    with col2:
        selected_tests = st.multiselect(label='Select QC Tests', options=ioos_qc_config['qartod'].keys())

    # Display options for selected test

    for current_test in selected_tests:

        test_config = ioos_qc_config['qartod'][current_test]
        test_label = 'Configure Test: ' + current_test
        #st.write(test_config)

        with st.expander(label=test_label, expanded=True):
            for current_param in test_config.keys():
                if isinstance(test_config[current_param], list):
                    col1, col2, col3, = st.columns([1,4,1])
                    with col1:
                        lower_bound = st.number_input(label='Override Lower Bound', value=min(test_config[current_param]))
                    with col2:
                        st.empty()
                    with col3:
                        upper_bound = st.number_input(label='Override Upper Bound', value=max(test_config[current_param]))
                    range = [upper_bound, lower_bound]

                    values = st.slider(label=current_param, value=range)
                    #st.write(values)
                    ioos_qc_config['qartod'][current_test][current_param] = values
                    #st.write(config)
                else:
                    # determine step
                    value = st.number_input(label=current_param, value=test_config[current_param])
                    ioos_qc_config['qartod'][current_test][current_param] = value
    
    if st.button(label='Run Tests'):
        write_config(ioos_qc_config)
        #open df?
        qartod_handler = QARTODHandler(df, ioos_qc_config)
        qartod_handler.run_tests(selected_column, tact_settings['timeField']['time'])
        result = qartod_handler.get_appended_results()
    
        if not result.empty:
            complete_flag = True
            st.success('Processing successful.')
            results_csv = convert_df(result)

            st.download_button(
                label="Download data as CSV",
                data=results_csv,
                file_name='results.csv',
                mime='text/csv',
            )
    if complete_flag:
        with st.expander(label='Explore Results'):
            display_qc_results(qartod_handler.get_results())