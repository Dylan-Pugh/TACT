# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/Users/DylanPugh/Development/TACT/tact/UI/qt/fileParserGUI.ui'
#
# Created by: PyQt5 UI code generator 5.15.7
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_parserMainWindow(object):
    def setupUi(self, parserMainWindow):
        parserMainWindow.setObjectName("parserMainWindow")
        parserMainWindow.resize(1055, 846)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(parserMainWindow.sizePolicy().hasHeightForWidth())
        parserMainWindow.setSizePolicy(sizePolicy)
        self.centralwidget = QtWidgets.QWidget(parserMainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.horizontalLayout_17 = QtWidgets.QHBoxLayout(self.centralwidget)
        self.horizontalLayout_17.setObjectName("horizontalLayout_17")
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.selectFileButton = QtWidgets.QPushButton(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.selectFileButton.sizePolicy().hasHeightForWidth())
        self.selectFileButton.setSizePolicy(sizePolicy)
        self.selectFileButton.setObjectName("selectFileButton")
        self.gridLayout.addWidget(self.selectFileButton, 0, 0, 1, 1)
        self.filePathLabel = QtWidgets.QLabel(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.filePathLabel.sizePolicy().hasHeightForWidth())
        self.filePathLabel.setSizePolicy(sizePolicy)
        self.filePathLabel.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.filePathLabel.setFrameShadow(QtWidgets.QFrame.Plain)
        self.filePathLabel.setObjectName("filePathLabel")
        self.gridLayout.addWidget(self.filePathLabel, 1, 0, 1, 1)
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.inputFileTextBox = QtWidgets.QPlainTextEdit(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.inputFileTextBox.sizePolicy().hasHeightForWidth())
        self.inputFileTextBox.setSizePolicy(sizePolicy)
        self.inputFileTextBox.setMaximumSize(QtCore.QSize(16777215, 27))
        self.inputFileTextBox.setBaseSize(QtCore.QSize(0, 40))
        self.inputFileTextBox.setObjectName("inputFileTextBox")
        self.horizontalLayout_4.addWidget(self.inputFileTextBox)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.concatButton = QtWidgets.QPushButton(self.centralwidget)
        self.concatButton.setEnabled(False)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.concatButton.sizePolicy().hasHeightForWidth())
        self.concatButton.setSizePolicy(sizePolicy)
        self.concatButton.setObjectName("concatButton")
        self.horizontalLayout_3.addWidget(self.concatButton)
        self.batchButton = QtWidgets.QPushButton(self.centralwidget)
        self.batchButton.setEnabled(False)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.batchButton.sizePolicy().hasHeightForWidth())
        self.batchButton.setSizePolicy(sizePolicy)
        self.batchButton.setObjectName("batchButton")
        self.horizontalLayout_3.addWidget(self.batchButton)
        self.horizontalLayout_4.addLayout(self.horizontalLayout_3)
        self.gridLayout.addLayout(self.horizontalLayout_4, 1, 1, 1, 1)
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 2, 0, 1, 1)
        self.outputFileTextBox = QtWidgets.QPlainTextEdit(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.outputFileTextBox.sizePolicy().hasHeightForWidth())
        self.outputFileTextBox.setSizePolicy(sizePolicy)
        self.outputFileTextBox.setMaximumSize(QtCore.QSize(16777215, 27))
        self.outputFileTextBox.setAcceptDrops(False)
        self.outputFileTextBox.setObjectName("outputFileTextBox")
        self.gridLayout.addWidget(self.outputFileTextBox, 2, 1, 1, 1)
        self.time_args_label = QtWidgets.QLabel(self.centralwidget)
        self.time_args_label.setObjectName("time_args_label")
        self.gridLayout.addWidget(self.time_args_label, 3, 0, 1, 1)
        self.horizontalLayout_9 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_9.setObjectName("horizontalLayout_9")
        self.fix_times_checkBox = QtWidgets.QCheckBox(self.centralwidget)
        self.fix_times_checkBox.setChecked(True)
        self.fix_times_checkBox.setObjectName("fix_times_checkBox")
        self.horizontalLayout_9.addWidget(self.fix_times_checkBox)
        self.fix_times_args = QtWidgets.QPlainTextEdit(self.centralwidget)
        self.fix_times_args.setMaximumSize(QtCore.QSize(16777215, 27))
        self.fix_times_args.setObjectName("fix_times_args")
        self.horizontalLayout_9.addWidget(self.fix_times_args)
        self.gridLayout.addLayout(self.horizontalLayout_9, 3, 1, 1, 1)
        self.resultsColumnLabel = QtWidgets.QLabel(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.resultsColumnLabel.sizePolicy().hasHeightForWidth())
        self.resultsColumnLabel.setSizePolicy(sizePolicy)
        self.resultsColumnLabel.setObjectName("resultsColumnLabel")
        self.gridLayout.addWidget(self.resultsColumnLabel, 4, 0, 1, 1)
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.resultsColumnTextBox = QtWidgets.QPlainTextEdit(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.resultsColumnTextBox.sizePolicy().hasHeightForWidth())
        self.resultsColumnTextBox.setSizePolicy(sizePolicy)
        self.resultsColumnTextBox.setMaximumSize(QtCore.QSize(16777215, 27))
        self.resultsColumnTextBox.setAcceptDrops(False)
        self.resultsColumnTextBox.setObjectName("resultsColumnTextBox")
        self.horizontalLayout_5.addWidget(self.resultsColumnTextBox)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.encodingLabel = QtWidgets.QLabel(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.encodingLabel.sizePolicy().hasHeightForWidth())
        self.encodingLabel.setSizePolicy(sizePolicy)
        self.encodingLabel.setObjectName("encodingLabel")
        self.horizontalLayout.addWidget(self.encodingLabel)
        self.encodingDropDown = QtWidgets.QComboBox(self.centralwidget)
        self.encodingDropDown.setEditable(False)
        self.encodingDropDown.setCurrentText("")
        self.encodingDropDown.setObjectName("encodingDropDown")
        self.horizontalLayout.addWidget(self.encodingDropDown)
        self.horizontalLayout_5.addLayout(self.horizontalLayout)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.resultsColumnPostionLabel = QtWidgets.QLabel(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.resultsColumnPostionLabel.sizePolicy().hasHeightForWidth())
        self.resultsColumnPostionLabel.setSizePolicy(sizePolicy)
        self.resultsColumnPostionLabel.setObjectName("resultsColumnPostionLabel")
        self.horizontalLayout_2.addWidget(self.resultsColumnPostionLabel)
        self.columnPositionSpinBox = QtWidgets.QSpinBox(self.centralwidget)
        self.columnPositionSpinBox.setObjectName("columnPositionSpinBox")
        self.horizontalLayout_2.addWidget(self.columnPositionSpinBox)
        self.horizontalLayout_5.addLayout(self.horizontalLayout_2)
        self.gridLayout.addLayout(self.horizontalLayout_5, 4, 1, 1, 1)
        self.dateFieldsLabel = QtWidgets.QLabel(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.dateFieldsLabel.sizePolicy().hasHeightForWidth())
        self.dateFieldsLabel.setSizePolicy(sizePolicy)
        self.dateFieldsLabel.setObjectName("dateFieldsLabel")
        self.gridLayout.addWidget(self.dateFieldsLabel, 5, 0, 1, 1)
        self.horizontalLayout_7 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_7.setObjectName("horizontalLayout_7")
        self.dateFieldsTextBox = QtWidgets.QPlainTextEdit(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.dateFieldsTextBox.sizePolicy().hasHeightForWidth())
        self.dateFieldsTextBox.setSizePolicy(sizePolicy)
        self.dateFieldsTextBox.setMaximumSize(QtCore.QSize(16777215, 27))
        self.dateFieldsTextBox.setAcceptDrops(False)
        self.dateFieldsTextBox.setObjectName("dateFieldsTextBox")
        self.horizontalLayout_7.addWidget(self.dateFieldsTextBox)
        self.horizontalLayout_6 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_6.setObjectName("horizontalLayout_6")
        self.timeFieldLabel = QtWidgets.QLabel(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.timeFieldLabel.sizePolicy().hasHeightForWidth())
        self.timeFieldLabel.setSizePolicy(sizePolicy)
        self.timeFieldLabel.setObjectName("timeFieldLabel")
        self.horizontalLayout_6.addWidget(self.timeFieldLabel)
        self.timeFieldTextBox = QtWidgets.QPlainTextEdit(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.timeFieldTextBox.sizePolicy().hasHeightForWidth())
        self.timeFieldTextBox.setSizePolicy(sizePolicy)
        self.timeFieldTextBox.setMaximumSize(QtCore.QSize(16777215, 27))
        self.timeFieldTextBox.setObjectName("timeFieldTextBox")
        self.horizontalLayout_6.addWidget(self.timeFieldTextBox)
        self.horizontalLayout_7.addLayout(self.horizontalLayout_6)
        self.gridLayout.addLayout(self.horizontalLayout_7, 5, 1, 1, 1)
        self.columnOutputLabel = QtWidgets.QLabel(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.columnOutputLabel.sizePolicy().hasHeightForWidth())
        self.columnOutputLabel.setSizePolicy(sizePolicy)
        self.columnOutputLabel.setMaximumSize(QtCore.QSize(16777215, 40))
        self.columnOutputLabel.setObjectName("columnOutputLabel")
        self.gridLayout.addWidget(self.columnOutputLabel, 6, 0, 1, 1)
        self.columnsTable = QtWidgets.QTableWidget(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.columnsTable.sizePolicy().hasHeightForWidth())
        self.columnsTable.setSizePolicy(sizePolicy)
        self.columnsTable.setMaximumSize(QtCore.QSize(16777215, 70))
        self.columnsTable.setBaseSize(QtCore.QSize(0, 40))
        self.columnsTable.setObjectName("columnsTable")
        self.columnsTable.setColumnCount(0)
        self.columnsTable.setRowCount(0)
        self.gridLayout.addWidget(self.columnsTable, 6, 1, 1, 1)
        self.previewButton = QtWidgets.QPushButton(self.centralwidget)
        self.previewButton.setEnabled(False)
        self.previewButton.setObjectName("previewButton")
        self.gridLayout.addWidget(self.previewButton, 7, 0, 1, 1)
        self.previewTable = QtWidgets.QTableWidget(self.centralwidget)
        self.previewTable.setObjectName("previewTable")
        self.previewTable.setColumnCount(0)
        self.previewTable.setRowCount(0)
        self.gridLayout.addWidget(self.previewTable, 7, 1, 1, 1)
        self.transformation_label = QtWidgets.QLabel(self.centralwidget)
        self.transformation_label.setObjectName("transformation_label")
        self.gridLayout.addWidget(self.transformation_label, 8, 0, 1, 1)
        self.horizontalLayout_14 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_14.setObjectName("horizontalLayout_14")
        self.delete_columns_checkBox = QtWidgets.QCheckBox(self.centralwidget)
        self.delete_columns_checkBox.setChecked(True)
        self.delete_columns_checkBox.setObjectName("delete_columns_checkBox")
        self.horizontalLayout_14.addWidget(self.delete_columns_checkBox)
        self.columns_to_delete_args = QtWidgets.QPlainTextEdit(self.centralwidget)
        self.columns_to_delete_args.setMaximumSize(QtCore.QSize(16777215, 27))
        self.columns_to_delete_args.setObjectName("columns_to_delete_args")
        self.horizontalLayout_14.addWidget(self.columns_to_delete_args)
        self.gridLayout.addLayout(self.horizontalLayout_14, 8, 1, 1, 1)
        self.select_all_button = QtWidgets.QPushButton(self.centralwidget)
        self.select_all_button.setEnabled(False)
        self.select_all_button.setObjectName("select_all_button")
        self.gridLayout.addWidget(self.select_all_button, 9, 0, 1, 1)
        self.horizontalLayout_13 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_13.setObjectName("horizontalLayout_13")
        self.replacement_Checkbox = QtWidgets.QCheckBox(self.centralwidget)
        self.replacement_Checkbox.setChecked(True)
        self.replacement_Checkbox.setObjectName("replacement_Checkbox")
        self.horizontalLayout_13.addWidget(self.replacement_Checkbox)
        self.replacement_args = QtWidgets.QPlainTextEdit(self.centralwidget)
        self.replacement_args.setMaximumSize(QtCore.QSize(16777215, 27))
        self.replacement_args.setObjectName("replacement_args")
        self.horizontalLayout_13.addWidget(self.replacement_args)
        self.gridLayout.addLayout(self.horizontalLayout_13, 9, 1, 1, 1)
        self.horizontalLayout_11 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_11.setObjectName("horizontalLayout_11")
        self.normalize_columns_checkBox = QtWidgets.QCheckBox(self.centralwidget)
        self.normalize_columns_checkBox.setChecked(True)
        self.normalize_columns_checkBox.setObjectName("normalize_columns_checkBox")
        self.horizontalLayout_11.addWidget(self.normalize_columns_checkBox)
        self.normalize_headers_args = QtWidgets.QPlainTextEdit(self.centralwidget)
        self.normalize_headers_args.setMaximumSize(QtCore.QSize(16777215, 27))
        self.normalize_headers_args.setObjectName("normalize_headers_args")
        self.horizontalLayout_11.addWidget(self.normalize_headers_args)
        self.gridLayout.addLayout(self.horizontalLayout_11, 10, 1, 1, 1)
        self.horizontalLayout_15 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_15.setObjectName("horizontalLayout_15")
        self.de_dupe_checkBox = QtWidgets.QCheckBox(self.centralwidget)
        self.de_dupe_checkBox.setChecked(True)
        self.de_dupe_checkBox.setObjectName("de_dupe_checkBox")
        self.horizontalLayout_15.addWidget(self.de_dupe_checkBox)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_15.addItem(spacerItem)
        self.gridLayout.addLayout(self.horizontalLayout_15, 11, 1, 1, 1)
        self.horizontalLayout_16 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_16.setObjectName("horizontalLayout_16")
        self.remove_columns_checkBox = QtWidgets.QCheckBox(self.centralwidget)
        self.remove_columns_checkBox.setChecked(True)
        self.remove_columns_checkBox.setObjectName("remove_columns_checkBox")
        self.horizontalLayout_16.addWidget(self.remove_columns_checkBox)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_16.addItem(spacerItem1)
        self.gridLayout.addLayout(self.horizontalLayout_16, 12, 1, 1, 1)
        self.processFileButton = QtWidgets.QPushButton(self.centralwidget)
        self.processFileButton.setEnabled(False)
        self.processFileButton.setObjectName("processFileButton")
        self.gridLayout.addWidget(self.processFileButton, 13, 0, 1, 1)
        self.horizontalLayout_8 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_8.setObjectName("horizontalLayout_8")
        self.fileProcessingProgressBar = QtWidgets.QProgressBar(self.centralwidget)
        self.fileProcessingProgressBar.setEnabled(True)
        self.fileProcessingProgressBar.setProperty("value", 0)
        self.fileProcessingProgressBar.setObjectName("fileProcessingProgressBar")
        self.horizontalLayout_8.addWidget(self.fileProcessingProgressBar)
        self.processingComplete = QtWidgets.QLabel(self.centralwidget)
        self.processingComplete.setEnabled(True)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.processingComplete.sizePolicy().hasHeightForWidth())
        self.processingComplete.setSizePolicy(sizePolicy)
        self.processingComplete.setMaximumSize(QtCore.QSize(40, 40))
        self.processingComplete.setText("")
        self.processingComplete.setPixmap(QtGui.QPixmap("/Users/DylanPugh/Development/TACT/tact/UI/qt/../../../Downloads/check-mark-button-emoji-clipart-xl.png"))
        self.processingComplete.setScaledContents(True)
        self.processingComplete.setObjectName("processingComplete")
        self.horizontalLayout_8.addWidget(self.processingComplete)
        self.gridLayout.addLayout(self.horizontalLayout_8, 13, 1, 1, 1)
        self.terminalOutputLabel = QtWidgets.QLabel(self.centralwidget)
        self.terminalOutputLabel.setObjectName("terminalOutputLabel")
        self.gridLayout.addWidget(self.terminalOutputLabel, 14, 0, 1, 1)
        self.terminalOutput = QtWidgets.QTextBrowser(self.centralwidget)
        self.terminalOutput.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.AdjustToContents)
        self.terminalOutput.setObjectName("terminalOutput")
        self.gridLayout.addWidget(self.terminalOutput, 14, 1, 1, 1)
        self.horizontalLayout_10 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_10.setObjectName("horizontalLayout_10")
        spacerItem2 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_10.addItem(spacerItem2)
        self.toQualityButton = QtWidgets.QPushButton(self.centralwidget)
        self.toQualityButton.setEnabled(False)
        self.toQualityButton.setMaximumSize(QtCore.QSize(200, 16777215))
        self.toQualityButton.setObjectName("toQualityButton")
        self.horizontalLayout_10.addWidget(self.toQualityButton)
        self.gridLayout.addLayout(self.horizontalLayout_10, 15, 1, 1, 1)
        self.horizontalLayout_17.addLayout(self.gridLayout)
        parserMainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(parserMainWindow)
        self.statusbar.setBaseSize(QtCore.QSize(0, 0))
        self.statusbar.setObjectName("statusbar")
        parserMainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(parserMainWindow)
        self.encodingDropDown.setCurrentIndex(-1)
        QtCore.QMetaObject.connectSlotsByName(parserMainWindow)

    def retranslateUi(self, parserMainWindow):
        _translate = QtCore.QCoreApplication.translate
        parserMainWindow.setWindowTitle(_translate("parserMainWindow", "TACT"))
        self.selectFileButton.setText(_translate("parserMainWindow", "Select File or Directory"))
        self.filePathLabel.setText(_translate("parserMainWindow", "Input Path:"))
        self.concatButton.setText(_translate("parserMainWindow", "Concatenate"))
        self.batchButton.setText(_translate("parserMainWindow", "Batch"))
        self.label.setText(_translate("parserMainWindow", "Output Path:"))
        self.time_args_label.setText(_translate("parserMainWindow", "Time Settings:"))
        self.fix_times_checkBox.setText(_translate("parserMainWindow", "Standardize Times"))
        self.resultsColumnLabel.setText(_translate("parserMainWindow", "Results Column:"))
        self.encodingLabel.setText(_translate("parserMainWindow", "Encoding:"))
        self.resultsColumnPostionLabel.setText(_translate("parserMainWindow", "Results Column Postion:"))
        self.dateFieldsLabel.setText(_translate("parserMainWindow", "Date Fields(s):"))
        self.timeFieldLabel.setText(_translate("parserMainWindow", "Time Field(s):"))
        self.columnOutputLabel.setText(_translate("parserMainWindow", "Column Names:"))
        self.previewButton.setText(_translate("parserMainWindow", "Preview"))
        self.transformation_label.setText(_translate("parserMainWindow", "Additional Transformations:"))
        self.delete_columns_checkBox.setText(_translate("parserMainWindow", "Delete Columns"))
        self.select_all_button.setText(_translate("parserMainWindow", "Select/Deselect All"))
        self.replacement_Checkbox.setText(_translate("parserMainWindow", "Replace in Rows"))
        self.normalize_columns_checkBox.setText(_translate("parserMainWindow", "Normalize Column Headers"))
        self.de_dupe_checkBox.setText(_translate("parserMainWindow", "Remove Duplicate Columns"))
        self.remove_columns_checkBox.setText(_translate("parserMainWindow", "Remove Empty Columns"))
        self.processFileButton.setText(_translate("parserMainWindow", "Process File"))
        self.terminalOutputLabel.setText(_translate("parserMainWindow", "Terminal Output:"))
        self.toQualityButton.setText(_translate("parserMainWindow", "Continue to Quality Check"))
