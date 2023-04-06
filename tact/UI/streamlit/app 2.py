import streamlit as st

# Custom imports
from multipage import MultiPage
from pages import data_upload, data_cleaner, data_report, ioos_qc_runner, data_transform



############################ Main App ############################

st.set_page_config(layout="wide")

# Create an instance of the app 
app = MultiPage()

# Web App Title & Header
col1, col2 = st.columns([1,6])

with col1:
    st.image('./front_end/assets/TACT-logos_white.png', use_column_width='auto')

with col2:
    st.markdown('''
    #
    Welcome to **TACT**, the **T**emporal **A**djustment **C**alculation **T**ool.

    **Credit:** App built in `Python` + `Streamlit` by [Dylan Pugh](https://github.com/Dylan-Pugh) at [GMRI](https://github.com/gulfofmaine).

    ---
    ''')

# Add all your applications (pages) here
app.add_page("Upload Data", data_upload.app)
app.add_page("Clean Dataset", data_cleaner.app)
app.add_page("Run IOOS QC", ioos_qc_runner.app)
app.add_page("Transform Dataset", data_transform.app)

#pandas profiling is broken
#app.add_page("Dataset Report", data_report.app)

# The main app
app.run()