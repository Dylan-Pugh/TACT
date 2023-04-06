import ast
import streamlit as st 
import control.controller as controller

# PLEASE be careful with this - Streamlit is very fickle
# For instance, one missing key will prevent ALL OTHER VALUES from syncing (for some reason)
# values here should be 1 to 1 synced with values in config/parserConfig.JSON
date_object_types = []

def write_settings():
    # syncs the Stremlit session state with TACT settings file
    # session state -> parserConfig.JSON
    #st.write(st.session_state)

    # check if we're in an initialized state
    if 'initialized' not in st.session_state:
        st.session_state['initialized'] = False
        
    if not st.session_state['initialized']:
        init_st_state()
        return

    # start with current settings from controller
    config_to_apply = controller.get_settings_json(config_type='parser')

    # update settings from session state, print success message
    config_to_apply["inputPath"] = st.session_state.inputPath
    config_to_apply["inputFileEncoding"] = st.session_state.inputFileEncoding
    config_to_apply["outputFilePath"] = st.session_state.outputFilePath
    config_to_apply["concatFiles"] = st.session_state.concatFiles
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
    date_object = st.session_state.dateFields
    date_object_types.append(type(date_object))

    if isinstance(st.session_state.dateFields, dict):
        config_to_apply["dateFields"] = st.session_state.dateFields
    else:
        config_to_apply["dateFields"] = ast.literal_eval(st.session_state.dateFields)
    
    if isinstance(st.session_state.timeField, dict):
        config_to_apply["timeField"] = st.session_state.timeField
    else:
        config_to_apply["timeField"] = ast.literal_eval(st.session_state.timeField)

    # write replacement args as JSON objects
    config_to_apply["headerValuesToReplace"] = st.session_state.headerValuesToReplace
    config_to_apply["rowValuesToReplace"] = st.session_state.rowValuesToReplace

    if isinstance(st.session_state.columnsToDelete, str):
        config_to_apply["columnsToDelete"] = st.session_state.columnsToDelete.split(',')
    else:
        config_to_apply["columnsToDelete"] = st.session_state.columnsToDelete

    controller.update_settings(config_type='parser', json_to_apply=config_to_apply)

def init_st_state():
    # start with current settings from controller
    settings_from_TACT = controller.get_settings_json(config_type='parser')

    for key in settings_from_TACT:
        if key not in st.session_state:
            st.session_state[key] = settings_from_TACT[key]
    
    st.session_state['initialized'] = True