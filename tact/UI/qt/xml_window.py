import json

from PyQt5 import QtCore, QtWidgets, uic

import tact.util.constants as constants
from tact.UI.fillable_field_widget import FillableFieldWidget
from tact.control.controller import get_xml_params, generate_xml
from tact.control.logging_controller import \
    LoggingController as loggingController

qt_creator_file = constants.XML_UI_FILE_PATH  # Enter file here.
Ui_MainWindow, QtBaseClass = uic.loadUiType(qt_creator_file)
logger = loggingController.get_logger(__name__)


class XMLWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    settings = constants.XML_CONFIG_PATH
    xml_lib = constants.XML_LIB_PATH
    processing = QtCore.pyqtSignal(int, name="value")
    switch_window = QtCore.pyqtSignal(int, name="value")

    def __init__(self):
        logger.info("Loading XML Generation window")
        QtWidgets.QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)

        self.backButton.clicked.connect(lambda: self.switch_window.emit(0))
        self.EDDTypecomboBox.currentIndexChanged.connect(
            self.display_list_of_params)
        # set up actions for:
        # Generate XML button clicked - gets all param values, updates settings, calls out to invoke
        # Results button clicked

        self.display_initial_settings(self)

        logger.info("XML Window init complete")

    def display_initial_settings(self):
        self.ERDDAPPathBox.setPlainText(constants.DEFAULT_ERDDAP_PATH)

        self.EDDTypecomboBox.addItems(self.xml_lib["EDDTypes"])
        self.EDDTypecomboBox.setCurrentIndex(
            self.xml_lib["EDDTypes"].index(
                constants.DEFAULT_EDD_TYPE))

    def display_list_of_params(self):
        get_xml_params(self.EDDTypecomboBox.currentText())
        params = self.config["parameters"]

        for current in params:
            to_add = FillableFieldWidget(
                current["prompt"],
                current["value"])
            self.paramList.addItem(to_add)

    def trigger_xml_generation(self):
        # iterate through param list,
        # update settings
        # call out to generate_xml
