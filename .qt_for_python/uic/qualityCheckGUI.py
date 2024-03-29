# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/Users/DylanPugh/Development/file-parser-GUI/tact/UI/qualityCheckGUI.ui'
#
# Created by: PyQt5 UI code generator 5.15.1
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_QAWindow(object):
    def setupUi(self, QAWindow):
        QAWindow.setObjectName("QAWindow")
        QAWindow.resize(1393, 616)
        self.centralwidget = QtWidgets.QWidget(QAWindow)
        self.centralwidget.setEnabled(True)
        self.centralwidget.setAutoFillBackground(False)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName("verticalLayout")
        self.gridLayout_2 = QtWidgets.QGridLayout()
        self.gridLayout_2.setSizeConstraint(QtWidgets.QLayout.SetMaximumSize)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.MaxDateBox = QtWidgets.QTextBrowser(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.MaxDateBox.sizePolicy().hasHeightForWidth())
        self.MaxDateBox.setSizePolicy(sizePolicy)
        self.MaxDateBox.setMinimumSize(QtCore.QSize(0, 27))
        self.MaxDateBox.setMaximumSize(QtCore.QSize(16777215, 27))
        self.MaxDateBox.setObjectName("MaxDateBox")
        self.gridLayout_2.addWidget(self.MaxDateBox, 0, 3, 1, 1)
        self.MinDateBox = QtWidgets.QTextBrowser(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.MinDateBox.sizePolicy().hasHeightForWidth())
        self.MinDateBox.setSizePolicy(sizePolicy)
        self.MinDateBox.setMinimumSize(QtCore.QSize(0, 27))
        self.MinDateBox.setMaximumSize(QtCore.QSize(16777215, 27))
        self.MinDateBox.setObjectName("MinDateBox")
        self.gridLayout_2.addWidget(self.MinDateBox, 0, 1, 1, 1)
        self.minDateLabel = QtWidgets.QLabel(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.minDateLabel.sizePolicy().hasHeightForWidth())
        self.minDateLabel.setSizePolicy(sizePolicy)
        self.minDateLabel.setMinimumSize(QtCore.QSize(0, 27))
        self.minDateLabel.setMaximumSize(QtCore.QSize(16777215, 27))
        self.minDateLabel.setObjectName("minDateLabel")
        self.gridLayout_2.addWidget(self.minDateLabel, 0, 0, 1, 1)
        self.MaxDateLabel = QtWidgets.QLabel(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.MaxDateLabel.sizePolicy().hasHeightForWidth())
        self.MaxDateLabel.setSizePolicy(sizePolicy)
        self.MaxDateLabel.setMinimumSize(QtCore.QSize(0, 27))
        self.MaxDateLabel.setMaximumSize(QtCore.QSize(16777215, 27))
        self.MaxDateLabel.setObjectName("MaxDateLabel")
        self.gridLayout_2.addWidget(self.MaxDateLabel, 0, 2, 1, 1)
        self.verticalLayout.addLayout(self.gridLayout_2)
        self.checkDivider = QtWidgets.QFrame(self.centralwidget)
        self.checkDivider.setMaximumSize(QtCore.QSize(16777215, 27))
        self.checkDivider.setFrameShape(QtWidgets.QFrame.HLine)
        self.checkDivider.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.checkDivider.setObjectName("checkDivider")
        self.verticalLayout.addWidget(self.checkDivider)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label_2 = QtWidgets.QLabel(self.centralwidget)
        self.label_2.setObjectName("label_2")
        self.horizontalLayout.addWidget(self.label_2)
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setObjectName("label")
        self.horizontalLayout.addWidget(self.label)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.checksList = QtWidgets.QListWidget(self.centralwidget)
        self.checksList.setUniformItemSizes(True)
        self.checksList.setObjectName("checksList")
        self.verticalLayout.addWidget(self.checksList)
        self.resultsTable = QtWidgets.QTableWidget(self.centralwidget)
        self.resultsTable.setObjectName("resultsTable")
        self.resultsTable.setColumnCount(0)
        self.resultsTable.setRowCount(0)
        self.verticalLayout.addWidget(self.resultsTable)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.progressLayout = QtWidgets.QHBoxLayout()
        self.progressLayout.setObjectName("progressLayout")
        self.progressLabel = QtWidgets.QLabel(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.progressLabel.sizePolicy().hasHeightForWidth())
        self.progressLabel.setSizePolicy(sizePolicy)
        self.progressLabel.setMaximumSize(QtCore.QSize(16777215, 27))
        self.progressLabel.setObjectName("progressLabel")
        self.progressLayout.addWidget(self.progressLabel)
        self.checkProgressBar = QtWidgets.QProgressBar(self.centralwidget)
        self.checkProgressBar.setMaximumSize(QtCore.QSize(16777215, 27))
        self.checkProgressBar.setProperty("value", 24)
        self.checkProgressBar.setObjectName("checkProgressBar")
        self.progressLayout.addWidget(self.checkProgressBar)
        self.horizontalLayout_2.addLayout(self.progressLayout)
        self.checksComplete = QtWidgets.QLabel(self.centralwidget)
        self.checksComplete.setEnabled(False)
        self.checksComplete.setMaximumSize(QtCore.QSize(40, 40))
        self.checksComplete.setText("")
        self.checksComplete.setPixmap(QtGui.QPixmap("/Users/DylanPugh/Development/file-parser-GUI/tact/UI/../../../../Downloads/check-mark-button-emoji-clipart-xl.png"))
        self.checksComplete.setScaledContents(True)
        self.checksComplete.setObjectName("checksComplete")
        self.horizontalLayout_2.addWidget(self.checksComplete)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.buttonLayout = QtWidgets.QHBoxLayout()
        self.buttonLayout.setObjectName("buttonLayout")
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.buttonLayout.addItem(spacerItem)
        self.backButton = QtWidgets.QPushButton(self.centralwidget)
        self.backButton.setObjectName("backButton")
        self.buttonLayout.addWidget(self.backButton)
        self.continueButton = QtWidgets.QPushButton(self.centralwidget)
        self.continueButton.setObjectName("continueButton")
        self.buttonLayout.addWidget(self.continueButton)
        self.verticalLayout.addLayout(self.buttonLayout)
        QAWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(QAWindow)
        self.statusbar.setObjectName("statusbar")
        QAWindow.setStatusBar(self.statusbar)

        self.retranslateUi(QAWindow)
        QtCore.QMetaObject.connectSlotsByName(QAWindow)

    def retranslateUi(self, QAWindow):
        _translate = QtCore.QCoreApplication.translate
        QAWindow.setWindowTitle(_translate("QAWindow", "MainWindow"))
        self.minDateLabel.setText(_translate("QAWindow", "Min Date"))
        self.MaxDateLabel.setText(_translate("QAWindow", "Max Date"))
        self.label_2.setText(_translate("QAWindow", "TextLabel"))
        self.label.setText(_translate("QAWindow", "TextLabel"))
        self.progressLabel.setText(_translate("QAWindow", "Progress:"))
        self.backButton.setText(_translate("QAWindow", "<- Back"))
        self.continueButton.setText(_translate("QAWindow", "Continue To XML Generation"))
