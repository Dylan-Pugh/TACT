# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/Users/DylanPugh/Development/file-parser-GUI/tact/UI/fillable_field_widget.ui'
#
# Created by: PyQt5 UI code generator 5.15.1
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
        self.label = QtWidgets.QLabel(Form)
        self.label.setObjectName("label")
        self.horizontalLayout.addWidget(self.label)
        self.value = QtWidgets.QTextEdit(Form)
        self.value.setMaximumSize(QtCore.QSize(16777215, 40))
        self.value.setAcceptDrops(False)
        self.value.setReadOnly(False)
        self.value.setObjectName("value")
        self.horizontalLayout.addWidget(self.value)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.label.setText(_translate("Form", "label"))
