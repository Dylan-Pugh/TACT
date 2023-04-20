import pandas as pd
import pandas_profiling
import streamlit as st
import control.controller as controller

from streamlit_pandas_profiling import st_profile_report


def app():
    config = controller.get_settings_json('parser')
    file_path = config['inputPath']

    df = pd.read_csv(file_path)
    pr = gen_profile_report(df, explorative=True)

    report_title = "Report for: " + file_path
    with st.expander(report_title, expanded=True):
        st_profile_report(pr)


@st.cache(allow_output_mutation=True)
def gen_profile_report(df, *report_args, **report_kwargs):
    return df.profile_report(*report_args, **report_kwargs)