import pandas as pd
import streamlit as st
import os



def highlight_rows(df):
    match_colors = {
    'exact':            '#4CAF50',  # green
    'exact_subgenus':  '#8BC34A',  # light green
    'phonetic':        '#FFEB3B',  # bright yellow
    'near_1':          '#FFC107',  # amber
    'near_2':          '#FF9800',  # orange
    'near_3':          '#F44336',  # red
    'match_quarantine': '#9E9E9E',  # gray
    'match_deleted':   '#BDBDBD'   # light gray
}
    
    # To highlight just the cells:
    #return df.style.applymap(lambda x: 'background-color: ' + match_colors[x] if x in match_colors else '')

    # To highlight the entire row
    return df.style.apply(lambda x: ['background-color: ' + match_colors[x['matchType']] if x['matchType'] in match_colors else ''] * len(df.columns), axis=1)


def display_match_preview(api_handle, preview_JSON):
    with st.form("taxon_preview_form"):
        taxon_preview = pd.DataFrame({k: {'Original': v['before'], **v['after']} for k, v in preview_JSON.items()}).T
        taxon_preview.insert(0, "accepted", False)

        st.write("Taxonomic Name Preview")
        preview_table = st.data_editor(
            data=highlight_rows(taxon_preview),
            disabled=[col for col in taxon_preview.columns if col != "accepted"],
            column_config={
                "accepted": st.column_config.CheckboxColumn(
                    "Accept Results?",
                    help="Select match for merge",
                    default=False,
                )
            },
            hide_index=True,
            use_container_width=True
            )

        submit_button = st.form_submit_button(label="Accept Selected Results")

    if submit_button:
        accepted_values = preview_table.loc[preview_table['accepted'], 'Original'].tolist()

        # Write settings
        outgoing_config = {
            "accepted_taxon_matches": accepted_values,
        }

        if api_handle.update_config(
            config_type="transform", config_to_apply=outgoing_config
        ):
            st.success(body=f"Config updated. Accepted values: {accepted_values}")
        else:
            st.error(body="Failed to update config.")


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
        #st.write(preview_JSON)
    else:
        st.error("Failed to match taxonomic names.")


display_match_preview(api_handle, preview_JSON)

transform_output_path = st.text_input(
    label="Output path for merge:", value=transform_config.get("transform_output_path")
)

if st.button(label="Merge Taxa Information"):
    if api_handle.update_config(
        config_type="transform", config_to_apply={"transform_output_path": transform_output_path}
    ):
        st.success("Config updated.")
    if api_handle.transform(operation="merge_taxa"):
        st.success("Success - taxonomic information merged.")
        st.balloons()
    else:
        st.error("Failed to merge taxa information.")

    st.download_button(
        label="Download merged data",
        data=pd.DataFrame.from_dict(api_handle.get_data(request_type="transform")).to_csv(index=False),
        file_name=os.path.basename(transform_output_path),
        mime='text/csv',
    )

        