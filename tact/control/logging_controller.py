import logging
import json
import tact.util.constants as constants
import tact.util.auto_log_handler as rotatingFileHandler


class LoggingController:

    with open(constants.LOG_CONFIG_PATH) as json_file:
        config = json.load(json_file)

    # create handlers
    file_handler = rotatingFileHandler.AutoReplacingFileHandler(
        constants.LOG_FILE_PATH, mode="w",
        backupCount=config.get("backupCount"))
    console_handler = logging.StreamHandler()

    # set levels
    console_handler.setLevel(config.get("logLevel"))
    file_handler.setLevel(config.get("logLevel"))

    # add formatters
    console_formatter = logging.Formatter(config.get("consoleFormatting"))
    file_formatter = logging.Formatter(config.get("fileFormatting"))
    console_handler.setFormatter(console_formatter)
    file_handler.setFormatter(file_formatter)

    def update_settings(self, settings):
        # write out settings file
        with open(constants.LOG_CONFIG_PATH, "w+") as outfile:
            json.dump(settings, outfile)

    @classmethod
    def get_logger(cls, name):
        # constuct logger
        logger = logging.getLogger(name)
        logger.addHandler(cls.file_handler)
        logger.addHandler(cls.console_handler)

        logger.setLevel(logging.DEBUG)

        return logger
