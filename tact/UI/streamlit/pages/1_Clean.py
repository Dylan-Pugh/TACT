import streamlit as st
import tact.util.constants as constants

######################## Helper Functions ########################


def display_analysis(config, api_handle):
    with st.form(key="settings_form"):
        # inputs/outputs
        col1, col2 = st.columns([4, 1])
        with col1:
            inputPath = st.text_input(
                key="inputPath", label="Input file path", value=config["inputPath"]
            )
        with col2:
            inputFileEncoding = st.selectbox(
                key="inputFileEncoding",
                label="File Encoding",
                options=constants.AVAILABLE_ENCODING_MODES,
            )

        col3, col4 = st.columns([4, 1])
        with col3:
            outputFilePath = st.text_input(
                key="outputFilePath",
                label="Output file path",
                value=config["outputFilePath"],
            )
        with col4:
            concatFiles = st.checkbox(
                key="concatFiles",
                label="Concatenate input files",
                disabled=not config["isDirectory"],
            )

        # parsed time settings
        col5, col6, col7 = st.columns([2, 4, 4])
        with col5:
            fixTimes = st.checkbox(
                key="fixTimes", label="Fix Times", value=config["fixTimes"]
            )
            deleteColumns = st.checkbox(
                key="deleteColumns",
                label="Delete Selected Columns",
                value=config["deleteColumns"],
            )
            normalizeHeaders = st.checkbox(
                key="normalizeHeaders",
                label="Normalize Headers",
                value=config["normalizeHeaders"],
            )
            replaceValues = st.checkbox(
                key="replaceValues",
                label="Replace Row Values",
                value=config["replaceValues"],
            )
            dropDuplicates = st.checkbox(
                key="dropDuplicates",
                label="Drop Duplicate Rows",
                value=config["dropDuplicates"],
            )
            dropEmpty = st.checkbox(
                key="dropEmpty", label="Drop Empty Columns", value=config["dropEmpty"]
            )
        with col6:
            parsedColumnName = st.text_input(
                key="parsedColumnName",
                label="Parsed Time Column Name",
                value=config["parsedColumnName"],
            )
            st.caption(body="Date Fields")
            dateFields = st.experimental_data_editor(
                key="dateFields",
                data=config["dateFields"],
                use_container_width=True,
                num_rows="dynamic",
            )
            st.caption(body="Header Values to Replace")

            updated_header_values = st.experimental_data_editor(
                key="headerValuesToReplace",
                data=config["headerValuesToReplace"],
                use_container_width=True,
                num_rows="dynamic",
            )
        with col7:
            parsedColumnPosition = st.number_input(
                key="parsedColumnPosition",
                label="Parsed Column Position",
                min_value=0,
                max_value=len(config["fieldNames"]),
            )
            st.caption(body="Time Fields")
            timeField = st.experimental_data_editor(
                key="timeField",
                data=config["timeField"],
                use_container_width=True,
                num_rows="dynamic",
            )

            st.caption(body="Row Values to Repalace")
            updated_row_values = st.experimental_data_editor(
                key="rowValuesToReplace",
                data=config["rowValuesToReplace"],
                use_container_width=True,
                num_rows="dynamic",
            )

        col8, col9 = st.columns([1, 4])

        aggregated_time_fields = list(config.get("dateFields").values()) + list(
            config.get("timeField").values()
        )

        with col9:
            columnsToDelete = st.multiselect(
                key="columnsToDelete",
                label="Columns To Delete",
                options=config.get("fieldNames"),
                default=aggregated_time_fields,
            )

        submit_button = st.form_submit_button(label="Update")

    if submit_button:
        # keys_to_write = config.keys()
        outgoing_config = {}

        keys_to_write = config.keys()

        for current_key in keys_to_write:
            if current_key == "headerValuesToReplace":
                outgoing_config["headerValuesToReplace"] = updated_header_values
            elif current_key == "rowValuesToReplace":
                outgoing_config["rowValuesToReplace"] = updated_row_values
            elif current_key == "dateFields":
                outgoing_config["dateFields"] = dateFields
            elif current_key == "timeField":
                outgoing_config["timeField"] = timeField
            else:
                if current_key in st.session_state:
                    outgoing_config[current_key] = st.session_state[current_key]

        # api call
        if api_handle.update_config(
            config_type="parser", config_to_apply=outgoing_config
        ):
            st.success(body="Config updated.")
        else:
            st.error(body="Failed to update config.")


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

# df will be null if inputPath is a directory
data_dict = api_handle.get_data(nrows=10)

# create_report(df)
if data_dict:
    with st.expander(label="Dataset Preview", expanded=True):
        st.table(data=data_dict)

with st.expander(label="Parser Settings", expanded=True):
    api_handle.analyze()
    display_analysis(config, api_handle)

with st.expander(label="Preview", expanded=True):
    if st.button(label="Preview Time Changes"):
        # on button press
        preview_JSON = api_handle.generate_preview()
        st.table(preview_JSON.get("samples"))

with st.expander(label="Process", expanded=True):
    if st.button(label="Process File(s)"):
        with st.spinner("Processing..."):
            api_handle.process()

        st.success(
            "Processing successful. Output file: " + st.session_state.outputFilePath
        )
        st.balloons()
