# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'create_good.ui'
#
# Created by: PyQt5 UI code generator 5.15.6
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(401, 103)
        self.gridLayout = QtWidgets.QGridLayout(Form)
        self.gridLayout.setObjectName("gridLayout")
        self.lineEdit_time_references = QtWidgets.QLineEdit(Form)
        self.lineEdit_time_references.setObjectName("lineEdit_time_references")
        self.gridLayout.addWidget(self.lineEdit_time_references, 1, 2, 1, 1)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.pushButton_save = QtWidgets.QPushButton(Form)
        self.pushButton_save.setObjectName("pushButton_save")
        self.horizontalLayout.addWidget(self.pushButton_save)
        self.gridLayout.addLayout(self.horizontalLayout, 2, 1, 1, 1)
        self.lineEdit_article = QtWidgets.QLineEdit(Form)
        self.lineEdit_article.setObjectName("lineEdit_article")
        self.gridLayout.addWidget(self.lineEdit_article, 1, 0, 1, 1)
        self.lineEdit_name = QtWidgets.QLineEdit(Form)
        self.lineEdit_name.setObjectName("lineEdit_name")
        self.gridLayout.addWidget(self.lineEdit_name, 1, 1, 1, 1)
        self.label = QtWidgets.QLabel(Form)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.label_2 = QtWidgets.QLabel(Form)
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_2, 0, 1, 1, 1)
        self.label_3 = QtWidgets.QLabel(Form)
        self.label_3.setObjectName("label_3")
        self.gridLayout.addWidget(self.label_3, 0, 2, 1, 1)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Добавление номенклатуры"))
        self.pushButton_save.setText(_translate("Form", "Сохранить"))
        self.label.setText(_translate("Form", "Артикул"))
        self.label_2.setText(_translate("Form", "Наименование"))
        self.label_3.setText(_translate("Form", "Время изготовления"))
