from PyQt5 import QtWidgets, uic
import tact.util.constants as constants

# Enter file here.
qt_creator_file = constants.FILLABLE_FIELD_WIDGET_UI_FILE_PATH
Ui_Widget, QtWidgets.QWidget = uic.loadUiType(qt_creator_file)


class FillableFieldWidget(QtWidgets.QListWidgetItem, Ui_Widget):
    def __init__(self, label, value):
        super().__init__()
        Ui_Widget.__init__(self)
        self.setupUi(self)

        self.check_label.setText(label)
        self.value.setText(value)
