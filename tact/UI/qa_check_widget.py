from PyQt5 import QtWidgets, uic
import tact.util.constants as constants
import json

qt_creator_file = constants.QA_CHECK_WIDGET_UI_FILE_PATH  # Enter file here.
Ui_Widget, QtWidgets.QWidget = uic.loadUiType(qt_creator_file)


class QACheckWidget(QtWidgets.QListWidgetItem, Ui_Widget):
    def __init__(self, enabled, label, description, arguments):
        QtWidgets.QListWidgetItem.__init__(self)
        Ui_Widget.__init__(self)
        self.setupUi(self)
        self.init_UI(self)

    def init_UI(self):
        self.enabled_checkbox.setChecked(self.enabled)
        self.check_label.setText(self.label)
        self.description.setText(self.description)
        self.arguments.setPlainText(json.dumps(self.arguments))
        self.pass_icon.hide()
