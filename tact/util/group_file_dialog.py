import os
from PyQt5 import QtWidgets


class GroupFileObjectDialog(QtWidgets.QFileDialog):

    def __init__(self, parent):
        super().__init__(parent)
        # self.setOption(QtWidgets.QFileDialog.DontUseNativeDialog)
        # self.setFileMode(QtWidgets.QFileDialog.Directory)
        self.currentChanged.connect(self._selected)

    def _selected(self, name):
        if os.path.isdir(name):
            self.setFileMode(QtWidgets.QFileDialog.Directory)
        else:
            self.setFileMode(QtWidgets.QFileDialog.ExistingFile)
