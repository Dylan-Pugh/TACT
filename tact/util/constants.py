UI_FILE_PATH = "/Users/DylanPugh/Development/file-parser-GUI/tact/UI/fileParserGUI.ui"
QA_UI_FILE_PATH = "/Users/DylanPugh/Development/file-parser-GUI/tact/UI/qualityCheckGUI.ui"
QA_CHECK_WIDGET_UI_FILE_PATH = "/Users/DylanPugh/Development/file-parser-GUI/tact/UI/qa_check_widget.ui"
XML_UI_FILE_PATH = "/Users/DylanPugh/Development/file-parser-GUI/tact/UI/xmlGenerationGUI.ui"
FILLABLE_FIELD_WIDGET_UI_FILE_PATH = "/Users/DylanPugh/Development/file-parser-GUI/tact/UI/fillable_field_widget.ui"
PARSER_CONFIG_FILE_PATH = "/Users/DylanPugh/Development/file-parser-GUI/tact/config/parserConfig.JSON"
LOG_CONFIG_PATH = "/Users/DylanPugh/Development/file-parser-GUI/tact/config/logConfig.JSON"
QA_CONFIG_PATH = "/Users/DylanPugh/Development/file-parser-GUI/tact/config/qaConfig.JSON"
XML_CONFIG_PATH = "/Users/DylanPugh/Development/file-parser-GUI/tact/config/generateDatasetsXmlConfig.JSON"
XML_LIB_PATH = "/Users/DylanPugh/Development/file-parser-GUI/tact/config/generateDatasetsXmlLib.JSON"
LOG_FILE_PATH = "/Users/DylanPugh/Development/file-parser-GUI/tact/logs/tact.log"
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
