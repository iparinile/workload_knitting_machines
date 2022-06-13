import sys

from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QTableWidgetItem

import create_good
import design
from queries import make_session, get_all_nomenclature, get_specifications_for_good, create_nomenclature


class MainWindow(QtWidgets.QMainWindow, design.Ui_MainWindow):
    def __init__(self):
        self.create_good_widget = None
        self.new_good_data = None
        super().__init__()
        self.setupUi(self)  # Это нужно для инициализации нашего дизайна

        self.pushButton_add_good.clicked.connect(self.open_create_good_widget)

        self.session = make_session()

        nomenclatures = get_all_nomenclature(self.session)
        row_counter = 0
        nomenclature_columns = ["id", "Артикул", "Наименование", "Характеристика", "Время изготовления, мин."]
        self.tableWidget_nomenclature.setColumnCount(len(nomenclature_columns))
        self.tableWidget_nomenclature.setHorizontalHeaderLabels(nomenclature_columns)

        row_count_table = 0
        for nomenclature in nomenclatures:
            specifications = get_specifications_for_good(self.session, nomenclature.id)
            if len(specifications) == 0:
                specifications = [""]
            for _ in specifications:
                row_count_table += 1

        self.tableWidget_nomenclature.setRowCount(row_count_table)

        for nomenclature in nomenclatures:
            specifications = get_specifications_for_good(self.session, nomenclature.id)
            if len(specifications) == 0:
                specifications = [""]
            for specification in specifications:
                article_item = QTableWidgetItem()
                article_item.setData(2, nomenclature.id)
                self.tableWidget_nomenclature.setItem(row_counter, 0, article_item)

                article_item = QTableWidgetItem()
                article_item.setData(2, nomenclature.article)
                self.tableWidget_nomenclature.setItem(row_counter, 1, article_item)

                name_item = QTableWidgetItem()
                name_item.setData(2, nomenclature.name)
                self.tableWidget_nomenclature.setItem(row_counter, 2, name_item)

                article_item = QTableWidgetItem()
                if specification == "":
                    article_item.setData(2, "")
                else:
                    article_item.setData(2, specification.name)
                self.tableWidget_nomenclature.setItem(row_counter, 3, article_item)

                time_references_item = QTableWidgetItem()
                time_references_item.setData(2, nomenclature.time_references)
                self.tableWidget_nomenclature.setItem(row_counter, 4, time_references_item)
                row_counter += 1

    def open_create_good_widget(self):
        self.create_good_widget = CreateNomenclatureWidget()

        self.create_good_widget.show()

        self.create_good_widget.pushButton_save.clicked.connect(self.create_good)

    def create_good(self):
        self.new_good_data = {
            "article": self.create_good_widget.lineEdit_article.text(),
            "name": self.create_good_widget.lineEdit_name.text(),
            "time_references": self.create_good_widget.lineEdit_time_references.text()
        }

        create_nomenclature(
            session=self.session,
            article=self.new_good_data["article"],
            name=self.new_good_data["name"],
            time_references=self.new_good_data["time_references"]
        )

        self.create_good_widget.hide()


class CreateNomenclatureWidget(QtWidgets.QWidget, create_good.Ui_Form):
    def __init__(self):
        super().__init__()
        self.setupUi(self)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)  # Новый экземпляр QApplication
    window = MainWindow()  # Создаём объект класса ExampleApp
    window.show()  # Показываем окно
    app.exec_()  # и запускаем приложение
