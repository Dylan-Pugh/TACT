from PyQt5 import QtWidgets, uic
import tact.util.constants as constants
import json

qt_creator_file = constants.QA_CHECK_WIDGET_UI_FILE_PATH  # Enter file here.
Ui_Widget, QtWidgets.QWidget = uic.loadUiType(qt_creator_file)


class QACheckWidget(QtWidgets.QListWidgetItem, Ui_Widget):
    def __init__(self, enabled, label, description, arguments):
        super().__init__()
        Ui_Widget.__init__(self)
        self.setupUi(self)

        self.enabled_checkbox.setChecked(enabled)
        self.check_label.setText(label)
        self.description.setText(description)
        self.arguments.setPlainText(json.dumps(arguments))
        self.pass_icon.hide()
