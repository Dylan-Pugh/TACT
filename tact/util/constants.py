CONFIG_TYPES = {"parser": "parser", "QA": "QA", "log": "log"}
CONFIG_FILE_PATHS = {
    "parser": "tact/config/parserConfig.JSON",
    "LOG_CONFIG_PATH": "tact/config/logConfig.JSON",
    "QA_CONFIG_PATH": "tact/config/qaConfig.JSON",
    "XML_CONFIG_PATH": "tact/config/generateDatasetsXmlConfig.JSON",
    "IOOS_QC_CONFIG_PATH": "tact/config/qc_configs/qc_config.json",
    "transform": "tact/config/transformConfig.JSON",
}
PARSER_CONFIG_FILE_PATH = (
    "tact/config/parserConfig.JSON"
)
LOG_CONFIG_PATH = "tact/config/logConfig.JSON"
QA_CONFIG_PATH = "tact/config/qaConfig.JSON"
XML_CONFIG_PATH = (
    "tact/config/generateDatasetsXmlConfig.JSON"
)
XML_LIB_PATH = (
    "tact/config/generateDatasetsXmlLib.JSON"
)
WORMS_LOOKUP_PATH = "tact/resources/worms_lut.csv"
LOG_FILE_PATH = "tact/logs/tact.log"
LOG_LEVELS = ["CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG"]
DEFAULT_LOG_LEVEL = "INFO"
DEFAULT_PARSED_COLUMN_NAME = "parsed_time"
DEFAULT_PARSED_COLUMN_POSITION = 0
DEFAULT_PARSED_COLUMN_FORMAT = "%Y-%m-%dT%H:%M:%S%z"
AVAILABLE_ENCODING_MODES = ["utf-8-sig", "ISO-8859-1"]
DEFAULT_ENCODING = "utf-8-sig"
DEFAULT_HEADER_REPLACEMENTS = [{"original": " ", "replacement": "_"}]
DEFAULT_ROW_VALUE_REPLACEMENTS = [
    {"original": "#DIV/0!", "replacement": ""},
    {"original": "#VALUE!", "replacement": ""},
    {"original": "#REF!", "replacement": ""},
]
DEFAULT_EDD_TYPE = "EDDTableFromAsciiFiles"
