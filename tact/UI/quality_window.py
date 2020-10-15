from PyQt5 import QtCore, QtWidgets, uic

import tact.util.constants as constants
from tact.control.logging_controller import \
    LoggingController as loggingController

qt_creator_file = constants.QA_UI_FILE_PATH  # Enter file here.
Ui_MainWindow, QtBaseClass = uic.loadUiType(qt_creator_file)
logger = loggingController.get_logger(__name__)


class QualityWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    settings = constants.PARSER_CONFIG_FILE_PATH
    processing = QtCore.pyqtSignal(int, name="value")
    switch_window = QtCore.pyqtSignal(int, name="value")

    def __init__(self):
        logger.info("Loading Quality Check window")
        QtWidgets.QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)

        self.backButton.clicked.connect(lambda: self.switch_window.emit(0))

        logger.info("Quality Check init complete")
