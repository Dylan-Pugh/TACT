UI_FILE_PATH = "/Users/DylanPugh/Development/TACT/tact/UI/fileParserGUI.ui"
QA_UI_FILE_PATH = "/Users/DylanPugh/Development/TACT/tact/UI/qualityCheckGUI.ui"
QA_CHECK_WIDGET_UI_FILE_PATH = "/Users/DylanPugh/Development/TACT/tact/UI/qa_check_widget.ui"
XML_UI_FILE_PATH = "/Users/DylanPugh/Development/TACT/tact/UI/xmlGenerationGUI.ui"
FILLABLE_FIELD_WIDGET_UI_FILE_PATH = "/Users/DylanPugh/Development/TACT/tact/UI/fillable_field_widget.ui"
#CONFIG_TYPES = {"parser": "parser", "QA": "QA", "log": "log"}
CONFIG_FILE_PATHS = {
    "parser": "/Users/DylanPugh/Development/TACT/tact/config/parserConfig.JSON",
    "LOG_CONFIG_PATH": "/Users/DylanPugh/Development/TACT/tact/config/logConfig.JSON",
    "QA_CONFIG_PATH": "/Users/DylanPugh/Development/TACT/tact/config/qaConfig.JSON",
    "XML_CONFIG_PATH": "/Users/DylanPugh/Development/TACT/tact/config/generateDatasetsXmlConfig.JSON"
}
PARSER_CONFIG_FILE_PATH = "/Users/DylanPugh/Development/TACT/tact/config/parserConfig.JSON"
LOG_CONFIG_PATH = "/Users/DylanPugh/Development/TACT/tact/config/logConfig.JSON"
QA_CONFIG_PATH = "/Users/DylanPugh/Development/TACT/tact/config/qaConfig.JSON"
XML_CONFIG_PATH = "/Users/DylanPugh/Development/TACT/tact/config/generateDatasetsXmlConfig.JSON"
XML_LIB_PATH = "/Users/DylanPugh/Development/TACT/tact/config/generateDatasetsXmlLib.JSON"
LOG_FILE_PATH = "/Users/DylanPugh/Development/TACT/tact/logs/tact.log"
LOG_LEVELS = ["CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG"]
DEFAULT_LOG_LEVEL = "INFO"
DEFAULT_PARSED_COLUMN_NAME = "parsed_time"
DEFAULT_PARSED_COLUMN_POSITION = 0
DEFAULT_PARSED_COLUMN_FORMAT = "%Y-%m-%dT%H:%M:%S%z"
AVAILABLE_ENCODING_MODES = ["utf-8-sig", "ISO-8859-1"]
DEFAULT_ENCODING = "utf-8-sig"
DEFAULT_HEADER_REPLACEMENTS = [
    {
        "original": " ",
        "replacement": "_"
    }
]
DEFAULT_ROW_VALUE_REPLACEMENTS = [
    {
        "original": "#DIV/0!",
        "replacement": ""
    },
    {
        "original": "#VALUE!",
        "replacement": ""
    },
    {
        "original": "#REF!",
        "replacement": ""
    }
]
DEFAULT_ERDDAP_PATH = "/Users/DylanPugh/Development/erddap/"
DEFAULT_EDD_TYPE = "EDDTableFromAsciiFiles"
