import pandas as pd
import streamlit as st




# Define a function to apply the colors
def highlight_rows(df):
    match_colors = {
    'exact': '#00FF00',  # bright green
    'exact_subgenus': '#32CD32',  # lime green
    'phonetic': '#C6F4D6',  # pale green
    'near_1': '#FFFF00',  # yellow
    'near_2': '#FFA07A',  # orange-yellow
    'near_3': '#FF0000',  # bright red
    'match_quarantine': '#808080',  # dark gray
    'match_deleted': '#C0C0C0'  # light gray
}
    
    # To highlight just the cells:
    #return df.style.applymap(lambda x: 'background-color: ' + match_colors[x] if x in match_colors else '')

    # To highlight the entire row
    return df.style.apply(lambda x: ['background-color: ' + match_colors[x['matchType']] if x['matchType'] in match_colors else ''] * len(df.columns), axis=1)


st.set_page_config(layout="wide", page_title="TACT: Bio Data Utils", page_icon=":dna:")

api_handle = st.session_state.api_handle

parser_config = api_handle.get_config(config_type="parser")
transform_config = api_handle.get_config(config_type="transform")

st.header("Biological Data Utilities", divider="rainbow")

input = st.text_input(
    label="Input File Path:", value=parser_config.get("inputPath")
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
Taxonomic Name Matching
---
Extract data in the target columns into discrete records (rows). Data in other columns will remain unchanged. You may also define constant values which will be added to every extracted row.
"""
)
# Allow users to select input columns & constants
target_data_column = st.selectbox(
    label="Select target column:",
    placeholder="Organism Name",
    options=list(data_dict.keys()),
)


if st.button(label="Match Taxonomic Names"):
    if api_handle.update_config(
        config_type="transform", config_to_apply={"target_column_for_taxon": target_data_column}
    ):
        st.success("Config updated.")
    with st.spinner("Matching..."):

        preview_JSON = api_handle.generate_preview(preview_type="taxonomic_names")
        if preview_JSON:
            st.success("Success - Taxonomic names matched")
            st.write(preview_JSON)

            taxon_preview = pd.DataFrame({k: {'Original': v['before'], **v['after']} for k, v in preview_JSON.items()}).T

            st.write("Taxonomic Name Preview")
            st.dataframe(data=highlight_rows(taxon_preview), hide_index=True, use_container_width=True)

        else:
            st.error("Failed to match taxonomic names.")