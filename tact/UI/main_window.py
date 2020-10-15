from PyQt5 import QtWidgets
import sys
import tact.UI.parser_window
import tact.UI.quality_window


class GUIMainWindow(QtWidgets.QStackedWidget):

    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        self.parser_window = tact.UI.parser_window.ParserWindow()
        self.qa_window = tact.UI.quality_window.QualityWindow()
        self.addWidget(self.parser_window)
        self.addWidget(self.qa_window)

        self.parser_window.switch_window.connect(self.setCurrentIndex)
        self.qa_window.switch_window.connect(self.setCurrentIndex)

        self.show


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = GUIMainWindow()
    window.show()
    sys.exit(app.exec_())
