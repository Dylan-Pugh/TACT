import streamlit as st
from settings_sync import write_settings

def app():
    # Upload CSV data
    st.file_uploader("Upload your input file", type=["csv","nc",], on_change=write_settings())

    # This is a workaround because Streamlit doesn't let you get the file path from an uploaded file :(
    placeholder = st.empty()

    input = placeholder.text_input('Input File Path:')

    col1, col2, col3 = st.columns([.5,1,8])
    with col1:
        submit_button = st.button('Submit')
    with col2:
        test_mode_button = st.button('Test Mode')
    with col3:
        st.empty()

    if submit_button:
        input = placeholder.text_input('Input File Path:', value=input, key=1)
        st.session_state['inputPath'] = input
        write_settings()
    if test_mode_button:
        input = placeholder.text_input('Input File Path:', value='testing/testData/TACT_test.csv', key=2)
        st.session_state['inputPath'] = input
        write_settings()