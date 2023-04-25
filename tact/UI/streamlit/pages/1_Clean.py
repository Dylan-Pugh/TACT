import streamlit as st
import tact.util.constants as constants
import tact.UI.streamlit.components.dict_table as dict_table
from settings_sync import write_settings

######################## Helper Functions ########################


def display_analysis(config):
    with st.form(key="settings_form"):
        # inputs/outputs
        col1, col2 = st.columns([4, 1])
        with col1:
            st.text_input(
                key="inputPath", label="Input file path", value=config["inputPath"]
            )
        with col2:
            st.selectbox(
                key="inputFileEncoding",
                label="File Encoding",
                options=constants.AVAILABLE_ENCODING_MODES,
            )

        col3, col4 = st.columns([4, 1])
        with col3:
            st.text_input(
                key="outputFilePath",
                label="Output file path",
                value=config["outputFilePath"],
            )
        with col4:
            st.checkbox(
                key="concatFiles",
                label="Concatenate input files",
                disabled=not config["isDirectory"],
            )

        # parsed time settings
        col5, col6, col7 = st.columns([2, 4, 4])
        with col5:
            st.checkbox(key="fixTimes", label="Fix Times", value=config["fixTimes"])
            st.checkbox(
                key="deleteColumns",
                label="Delete Selected Columns",
                value=config["deleteColumns"],
            )
            st.checkbox(
                key="normalizeHeaders",
                label="Normalize Headers",
                value=config["normalizeHeaders"],
            )
            st.checkbox(
                key="replaceValues",
                label="Replace Row Values",
                value=config["replaceValues"],
            )
            st.checkbox(
                key="dropDuplicates",
                label="Drop Duplicate Rows",
                value=config["dropDuplicates"],
            )
            st.checkbox(
                key="dropEmpty", label="Drop Empty Columns", value=config["dropEmpty"]
            )
        with col6:
            st.text_input(
                key="parsedColumnName",
                label="Parsed Time Column Name",
                value=config["parsedColumnName"],
            )
            st.text_input(
                key="dateFields", label="Date Fields", value=config["dateFields"]
            )
        with col7:
            st.number_input(
                key="parsedColumnPosition",
                label="Parsed Column Position",
                min_value=0,
                max_value=len(config["fieldNames"]),
            )
            st.text_input(
                key="timeField", label="Time Fields", value=config["timeField"]
            )

        # handling for multiple date/time fields

        # Autofills date/time fields into columnsToDelete
        columns_to_delete_args = ""
        for key, value in config["dateFields"].items():
            if config["dateFields"].get(key) != "Not Found":
                if columns_to_delete_args == "":
                    columns_to_delete_args += config["dateFields"].get(key)
                else:
                    columns_to_delete_args += "," + config["dateFields"].get(key)
        for key, value in config["timeField"].items():
            if config["timeField"].get(key) != "Not Found":
                if columns_to_delete_args == "":
                    columns_to_delete_args += config["timeField"].get(key)
                else:
                    columns_to_delete_args += "," + config["timeField"].get(key)

        col8, col9 = st.columns([1, 4])
        # with col6:
        #     st.checkbox(key='deleteColumns', label='Delete Selected Columns', value=config["deleteColumns"])
        #     st.checkbox(key='normalizeHeaders', label='Normalize Headers', value=config["normalizeHeaders"])
        #     st.checkbox(key='replaceValues', label='Replace Row Values', value=config["replaceValues"])
        with col9:
            st.text_input(
                key="columnsToDelete",
                label="Columns To Delete",
                value=columns_to_delete_args,
            )
            # st.text_input(
            #     key="headerValuesToReplace",
            #     label="Header Values to Replace",
            #     value=json.dumps(config["headerValuesToReplace"]),
            # )
            # st.text_input(
            #     key="rowValuesToReplace",
            #     label="Row Values to Replace",
            #     value=json.dumps(config["rowValuesToReplace"]),
            # )

        # Additional fixes
        # st.checkbox(key='dropDuplicates', label='Drop Duplicate Rows', value=config["dropDuplicates"])
        # st.checkbox(key='dropEmpty', label='Drop Empty Rows', value=config["dropEmpty"])

        st.form_submit_button(label="Update", on_click=write_settings)

    col1, col2 = st.columns([4, 4])
    with col1:
        header_vals = dict_table.DictTable(
            input_dict=config["headerValuesToReplace"],
            top_level_dict="headerValuesToReplace",
            label="Header Values to Replace",
            key_label="Original",
            value_label="Replacement",
        )
        header_vals.render()

    with col2:
        row_vals = dict_table.DictTable(
            input_dict=config["rowValuesToReplace"],
            top_level_dict="rowValuesToReplace",
            label="Row Values to Replace",
            key_label="Original",
            value_label="Replacement",
        )
        row_vals.render()

    print_state = st.button(label="Print State")
    if print_state:
        st.write(st.session_state)


def display_preview(preview_JSON):
    # st.write(preview_JSON)
    st.table(preview_JSON)
    return


############################ Main App ############################
st.set_page_config(layout="wide", page_title="TACT: Clean", page_icon=":broom:")

api_handle = st.session_state.api_handle

st.markdown(
    """
#
Operations for Cleaning Input Data
---
"""
)

config = api_handle.get_config(config_type="parser")

file_path = config["inputPath"]

# df will be null if inputPath is a directory
data_dict = api_handle.get_data(nrows=10)

# create_report(df)
if data_dict:
    with st.expander(label="Dataset Preview", expanded=True):
        st.table(data=data_dict)

with st.expander(label="Parser Settings", expanded=True):
    api_handle.analyze()
    # config = controller.get_settings_json('parser')
    display_analysis(config)

with st.expander(label="Preview", expanded=True):
    if st.button(label="Preview Time Changes"):
        # on button press
        write_settings()
        preview_JSON = api_handle.generate_preview()
        display_preview(preview_JSON.get("samples"))

with st.expander(label="Process", expanded=True):
    if st.button(label="Process File(s)"):
        write_settings()
        with st.spinner("Processing..."):
            api_handle.process()

        st.success(
            "Processing successful. Output file: " + st.session_state.outputFilePath
        )
        st.balloons()
