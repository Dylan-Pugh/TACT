# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/Users/DylanPugh/Development/TACT/tact/UI/qt/qa_check_widget.ui'
#
# Created by: PyQt5 UI code generator 5.15.7
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(822, 118)
        self.horizontalLayout = QtWidgets.QHBoxLayout(Form)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.enabled_checkbox = QtWidgets.QCheckBox(Form)
        self.enabled_checkbox.setText("")
        self.enabled_checkbox.setObjectName("enabled_checkbox")
        self.horizontalLayout.addWidget(self.enabled_checkbox)
        self.check_label = QtWidgets.QLabel(Form)
        self.check_label.setObjectName("check_label")
        self.horizontalLayout.addWidget(self.check_label)
        self.description = QtWidgets.QTextEdit(Form)
        self.description.setMaximumSize(QtCore.QSize(16777215, 40))
        self.description.setAcceptDrops(False)
        self.description.setReadOnly(False)
        self.description.setObjectName("description")
        self.horizontalLayout.addWidget(self.description)
        self.arguments = QtWidgets.QTextEdit(Form)
        self.arguments.setMaximumSize(QtCore.QSize(16777215, 40))
        self.arguments.setObjectName("arguments")
        self.horizontalLayout.addWidget(self.arguments)
        self.pass_icon = QtWidgets.QLabel(Form)
        self.pass_icon.setMaximumSize(QtCore.QSize(40, 40))
        self.pass_icon.setText("")
        self.pass_icon.setPixmap(QtGui.QPixmap("/Users/DylanPugh/Development/TACT/tact/UI/qt/../../../../Downloads/check-mark-button-emoji-clipart-xl.png"))
        self.pass_icon.setScaledContents(True)
        self.pass_icon.setObjectName("pass_icon")
        self.horizontalLayout.addWidget(self.pass_icon)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.check_label.setText(_translate("Form", "checkName"))
