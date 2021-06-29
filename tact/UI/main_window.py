from PyQt5 import QtWidgets
import sys
import tact.UI.parser_window
import tact.UI.quality_window
import tact.control.controller as controller


class GUIMainWindow(QtWidgets.QStackedWidget):

    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        self.parser_window = tact.UI.parser_window.ParserWindow()
        self.qa_window = tact.UI.quality_window.QualityWindow()
        self.addWidget(self.parser_window)
        self.addWidget(self.qa_window)

        self.parser_window.switch_window.connect(self.setCurrentIndex)
        self.parser_window.switch_window.connect(self.init_quality_window)

        self.qa_window.switch_window.connect(self.setCurrentIndex)

        self.currentChanged.connect(self.init_quality_window)

        self.show

    def init_quality_window(self):
        if self.currentIndex() == 1:
            controller.init_quality_check()
            self.qa_window.display_initial_settings()
            self.qa_window.display_list_of_checks()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = GUIMainWindow()
    window.show()
    sys.exit(app.exec_())
