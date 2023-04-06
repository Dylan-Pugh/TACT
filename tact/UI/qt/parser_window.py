import json
import sys

from PyQt5 import QtCore, QtGui, QtWidgets, uic

import tact.control.controller as controller
import tact.util.constants as constants
import tact.util.group_file_dialog as groupFileDialog
import tact.util.outlog as outlog
from tact.control.logging_controller import \
    LoggingController as loggingController

qt_creator_file = constants.UI_FILE_PATH  # Enter file here.
Ui_MainWindow, QtBaseClass = uic.loadUiType(qt_creator_file)
logger = loggingController.get_logger(__name__)


class ParserWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    input_file_name = "not found"
    settings = constants.PARSER_CONFIG_FILE_PATH
    processing = QtCore.pyqtSignal(int, name="value")
    switch_window = QtCore.pyqtSignal(int, name="index")

    def __init__(self):
        logger.info("TACT: The Temporal Adjustment Calculation Tool")
        logger.info("TACT - Start")
        QtWidgets.QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)
        self.selectFileButton.clicked.connect(self.get_file)
        self.processFileButton.clicked.connect(self.invoke_parser)
        self.previewButton.clicked.connect(self.display_preview)
        self.fileProcessingProgressBar.setValue(0)
        self.fileProcessingProgressBar.setMaximum(100)
        self.processing.connect(self.fileProcessingProgressBar.setValue)
        self.processingComplete.hide()
        self.concatButton.clicked.connect(self.concatenate)
        self.batchButton.clicked.connect(self.batch_process)
        self.encodingDropDown.addItems(constants.AVAILABLE_ENCODING_MODES)
        self.encodingDropDown.setCurrentIndex(
            constants.AVAILABLE_ENCODING_MODES.index(
                constants.DEFAULT_ENCODING))
        self.select_all_button.clicked.connect(self.toggle_checks)
        self.toQualityButton.clicked.connect(
            lambda: self.switch_window.emit(1))
        # TODO: For testing purposes:
        self.toQualityButton.setEnabled(True)

        logger.info("GUI initialization complete")

    def get_file(self):
        # open file
        open_dialog = groupFileDialog.GroupFileObjectDialog(self)

        open_dialog.exec_()
        fname = open_dialog.selectedFiles()
        logger.info("File selected: %s", fname)

        if controller.is_directory(fname[0]):
            # pause processing until user clicks concatenate button
            logger.info(
                "Input path is a directory - execution paused until user selects 'Batch' or 'Concatenate'")
            self.concatButton.setEnabled(True)
            self.batchButton.setEnabled(True)
            self.inputFileTextBox.setPlainText(fname[0])
            self.input_file_name = fname[0]
            return
        else:
            self.input_file_name = fname[0]

        logger.info("Invoking Analyzer")
        self.settings = controller.analyze(self.input_file_name)
        logger.info("Displaying Analysis")
        self.display_analysis(self.settings)

        self.select_all_button.setEnabled(True)
        self.processFileButton.setEnabled(True)

    def concatenate(self):
        # inputFileName starts as a directory, is then updated to point to
        # combined file
        self.input_file_name = controller.concat_files(self.input_file_name)
        self.outputFileTextBox.setPlainText(self.input_file_name)

        self.settings = controller.analyze(self.input_file_name)
        self.display_analysis(self.settings)

        self.processFileButton.setEnabled(True)

    def batch_process(self):
        logger.info("Proceeding with batch processing")
        self.outputFileTextBox.setPlainText(self.input_file_name)

        # Doesn't actually update settings file - overwritten with call to display_analysis, which loads the file
        # Need to actually update the settings file
        self.settings = controller.analyze(self.input_file_name)
        self.display_analysis(self.settings)

        self.processFileButton.setEnabled(True)

    def display_analysis(self, settings_JSON):
        with open(settings_JSON) as json_file:
            config = json.load(json_file)

            self.inputFileTextBox.setPlainText(config["inputPath"])
            self.outputFileTextBox.setPlainText(config["outputFilePath"])
            self.resultsColumnTextBox.setPlainText(config["parsedColumnName"])
            self.columnPositionSpinBox.setRange(
                0, len(config["fieldNames"]))
            self.columnPositionSpinBox.setValue(config["parsedColumnPosition"])

            # Handling for multiple date/time fields
            self.dateFieldsTextBox.setPlainText(
                json.dumps(config["dateFields"]))
            self.timeFieldTextBox.setPlainText(json.dumps(config["timeField"]))

            # Autofills date/time fields into columnsToDelete
            columns_to_delete_args = ""
            for key, value in config["dateFields"].items():
                if config["dateFields"].get(key) != "Not Found":
                    if columns_to_delete_args == "":
                        columns_to_delete_args += config["dateFields"].get(key)
                    else:
                        columns_to_delete_args += ("," +
                                                   config["dateFields"].get(key))
            for key, value in config["timeField"].items():
                if config["timeField"].get(key) != "Not Found":
                    if columns_to_delete_args == "":
                        columns_to_delete_args += config["timeField"].get(key)
                    else:
                        columns_to_delete_args += ("," +
                                                   config["timeField"].get(key))
            self.columns_to_delete_args.setPlainText(
                columns_to_delete_args)

            # set up table for column names
            column_names = config["fieldNames"]
            self.columnsTable.setColumnCount(len(column_names))
            self.columnsTable.setRowCount(1)

            for index, value in enumerate(column_names):
                self.columnsTable.setItem(
                    0, index, QtWidgets.QTableWidgetItem(value))

            self.normalize_headers_args.setPlainText(
                json.dumps(config["headerValuesToReplace"]))
            self.replacement_args.setPlainText(
                json.dumps(config["rowValuesToReplace"]))
            # self.columns_to_delete_args.setPlainText(
            #  ",".join(config["columnsToDelete"]))

        self.previewButton.setEnabled(True)

    def display_preview(self):
        # first save any changes to settings JSON
        self.update_settings()

        preview_JSON = controller.generate_preview(self.settings)

        sample_list = preview_JSON["samples"]
        header_list = list(sample_list[0].keys())
        # set the row & column count, as well as headers
        # row count is the number of samples
        # column count is the number of fields in each sample object
        # headers are the keys of a sample object
        self.previewTable.setRowCount(len(sample_list))
        self.previewTable.setColumnCount((len(sample_list[0])))
        # replaces underscores with spaces to make headers look nicer -
        # underlying JSON is not affected
        self.previewTable.setHorizontalHeaderLabels(
            list(map(lambda current: current.replace("_", " "), header_list))
        )

        # populate the table
        # outer loop: list of samples
        # inner loop: list of fields in an individual sample
        for index, value in enumerate(sample_list):
            for key in value.keys():
                header_index = header_list.index(key)
                self.previewTable.setItem(
                    index, header_index, QtWidgets.QTableWidgetItem(value[key])
                )

    def invoke_parser(self):
        # first thing this needs to do is update(write) the settings JSON
        self.update_settings()

        sys.stdout = outlog.OutLog(self.terminalOutput, sys.stdout)
        sys.stderr = outlog.OutLog(
            self.terminalOutput, sys.stderr, QtGui.QColor(255, 0, 0)
        )

        controller.process()

        # emit signal for progress bar
        self.processing.emit(100)
        self.processingComplete.show()

        self.toQualityButton.setEnabled(True)

    def toggle_checks(self):
        self.de_dupe_checkBox.setChecked(
            not self.de_dupe_checkBox.isChecked())

        self.remove_columns_checkBox.setChecked(
            not self.remove_columns_checkBox.isChecked())

        self.normalize_columns_checkBox.setChecked(
            not self.normalize_columns_checkBox.isChecked())

        self.replacement_Checkbox.setChecked(
            not self.replacement_Checkbox.isChecked())

        self.delete_columns_checkBox.setChecked(
            not self.delete_columns_checkBox.isChecked())

    def update_settings(self):
        with open(self.settings, "r") as json_file:
            config = json.load(json_file)

            config["inputPath"] = self.inputFileTextBox.toPlainText()
            config["inputFileEncoding"] = self.encodingDropDown.currentText()
            config["outputFilePath"] = self.outputFileTextBox.toPlainText()
            config["parsedColumnName"] = self.resultsColumnTextBox.toPlainText()
            config["parsedColumnPosition"] = self.columnPositionSpinBox.value()

            # Checks to perform
            config["dropDuplicates"] = True if self.de_dupe_checkBox.isChecked(
            ) else False

            config["fixTimes"] = True if self.fix_times_checkBox.isChecked() else False

            config["dropEmpty"] = True if self.remove_columns_checkBox.isChecked(
            ) else False

            config["normalizeHeaders"] = True if self.normalize_columns_checkBox.isChecked(
            ) else False

            config["replaceValues"] = True if self.replacement_Checkbox.isChecked(
            ) else False

            config["deleteColumns"] = True if self.delete_columns_checkBox.isChecked(
            ) else False

            # write time & date fields as a JSON object
            config["dateFields"] = json.loads(
                self.dateFieldsTextBox.toPlainText())
            config["timeField"] = json.loads(
                self.timeFieldTextBox.toPlainText())

            # write replacement args as JSON objects
            config["headerValuesToReplace"] = json.loads(
                self.normalize_headers_args.toPlainText())
            config["rowValuesToReplace"] = json.loads(
                self.replacement_args.toPlainText())

            config["columnsToDelete"] = self.columns_to_delete_args.toPlainText().split(
                ',')

            controller.update_settings(
                config, constants.PARSER_CONFIG_FILE_PATH)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = ParserWindow()
    window.show()
    sys.exit(app.exec_())
