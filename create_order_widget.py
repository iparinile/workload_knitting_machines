# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'create_order.ui'
#
# Created by: PyQt5 UI code generator 5.15.6
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(322, 91)
        self.gridLayout = QtWidgets.QGridLayout(Form)
        self.gridLayout.setObjectName("gridLayout")
        self.lineEdit_amount = QtWidgets.QLineEdit(Form)
        self.lineEdit_amount.setObjectName("lineEdit_amount")
        self.gridLayout.addWidget(self.lineEdit_amount, 1, 1, 1, 1)
        self.label = QtWidgets.QLabel(Form)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.label_2 = QtWidgets.QLabel(Form)
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_2, 0, 1, 1, 1)
        self.lineEdit_order_id = QtWidgets.QLineEdit(Form)
        self.lineEdit_order_id.setObjectName("lineEdit_order_id")
        self.gridLayout.addWidget(self.lineEdit_order_id, 1, 0, 1, 1)
        self.pushButton_save = QtWidgets.QPushButton(Form)
        self.pushButton_save.setObjectName("pushButton_save")
        self.gridLayout.addWidget(self.pushButton_save, 2, 0, 1, 2)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Добавление заказа"))
        self.label.setText(_translate("Form", "Номер заказа"))
        self.label_2.setText(_translate("Form", "Количество"))
        self.pushButton_save.setText(_translate("Form", "Сохранить"))
