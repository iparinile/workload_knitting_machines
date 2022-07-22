import sys

from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QTableWidgetItem

import create_good

import create_order_widget
import create_characteristic_widget
import design
from queries import make_session, get_all_nomenclature, get_characteristic_for_good, create_nomenclature, \
    get_grouped_loading_of_machines, get_info_about_characteristic_in_order, get_order_by_one_c_id, create_order, \
    create_order_with_date_load, create_characteristic


class MainWindow(QtWidgets.QMainWindow, design.Ui_MainWindow):
    def __init__(self):
        self.create_good_widget = None
        self.create_characteristic_widget = None
        self.create_order_widget = None
        self.new_good_data = None
        super().__init__()
        self.setupUi(self)  # Это нужно для инициализации нашего дизайна

        self.pushButton_add_good.clicked.connect(self.open_create_good_widget)
        self.pushButton_add_characteristic.clicked.connect(self.open_create_characteristic_widget)
        self.pushButton_add_order_to_select_nomenclature.clicked.connect(self.open_create_order_widget)

        self.session = make_session()

        self.get_all_nomenclature()
        self.tableWidget_nomenclature.resizeColumnsToContents()
        self.get_loading_of_machines()

    def open_create_characteristic_widget(self):
        self.create_characteristic_widget = CreateCharacteristicWidget()

        self.create_characteristic_widget.show()

        self.create_characteristic_widget.pushButton_save.clicked.connect(self.create_new_characteristic)

    def create_new_characteristic(self):
        current_row_index = self.tableWidget_nomenclature.currentRow()
        good_id = self.tableWidget_nomenclature.item(current_row_index, 1).data(100)
        characteristic_name = self.create_characteristic_widget.lineEdit_characteristic_name.text()

        # Сделать проверку на наличие спецификации
        # db_specification = get_order_by_one_c_id(self.session, order_one_c_id)

        create_characteristic(self.session, characteristic_name, good_id)
        self.get_all_nomenclature()
        self.create_characteristic_widget.hide()

    def open_create_order_widget(self):
        self.create_order_widget = CreateOrderWidget()

        self.create_order_widget.show()

        self.create_order_widget.pushButton_save.clicked.connect(self.create_new_order)

    def create_new_order(self):
        current_row_index = self.tableWidget_nomenclature.currentRow()
        characteristic_id = self.tableWidget_nomenclature.item(current_row_index, 2).data(100)
        order_one_c_id = self.create_order_widget.lineEdit_order_id.text()
        characteristic_amount = int(self.create_order_widget.lineEdit_amount.text())

        db_order = get_order_by_one_c_id(self.session, order_one_c_id)

        if db_order is None:
            db_order = create_order(self.session, order_one_c_id)

        create_order_with_date_load(self.session, db_order.id, characteristic_id, characteristic_amount)
        self.create_order_widget.hide()
        self.get_loading_of_machines()

    def get_loading_of_machines(self):
        all_loading_machines_data = get_grouped_loading_of_machines(self.session)
        for machines_id in all_loading_machines_data.keys():
            machine_load_data = all_loading_machines_data[machines_id]
            machines_sheet = self.tableWidget_5_grade  # Придумать заглушку
            if machines_id == 1:
                machines_sheet = self.tableWidget_5_grade
            elif machines_id == 2:
                machines_sheet = self.tableWidget_7_grade
            elif machines_id == 3:
                machines_sheet = self.tableWidget_10_grade
            elif machines_id == 4:
                machines_sheet = self.tableWidget_12_grade
            elif machines_id == 5:
                machines_sheet = self.tableWidget_12_1_grade

            max_row_counter = 0  # Поиск наибольшего количества строк
            for work_data in machine_load_data:
                if len(work_data["load_machine_data"]) > max_row_counter:
                    max_row_counter = len(work_data["load_machine_data"])
            column_counter = len(machine_load_data)

            machines_sheet.setRowCount(max_row_counter)
            machines_sheet.setColumnCount(column_counter)

            column_headers = []
            for db_date_load in machine_load_data:
                column_headers.append(db_date_load['date'].strftime('%d.%m.%Y'))

            machines_sheet.setHorizontalHeaderLabels(column_headers)

            column_counter = 0
            for work_date_info in machine_load_data:
                row_counter = 0
                for db_load_machine in work_date_info['load_machine_data']:
                    load_data_item = QTableWidgetItem()
                    characteristic_info = get_info_about_characteristic_in_order(
                        self.session,
                        db_load_machine.characteristic_in_order_id)
                    load_data_item.setData(2,
                                           f"Заказ {characteristic_info['order_number']}, "
                                           f"{characteristic_info['article']} "
                                           f"{characteristic_info['nomenclature_name']}"
                                           f", {characteristic_info['characteristic_name']}, "
                                           f"время - {db_load_machine.time_references} минут")
                    machines_sheet.setItem(row_counter, column_counter, load_data_item)

                    row_counter += 1
                column_counter += 1

            machines_sheet.resizeColumnsToContents()

    def get_all_nomenclature(self):
        nomenclatures = get_all_nomenclature(self.session)
        row_counter = 0
        nomenclature_columns = ["Артикул", "Номенклатура", "Характеристика", "Время изготовления, мин."]
        self.tableWidget_nomenclature.setColumnCount(len(nomenclature_columns))
        self.tableWidget_nomenclature.setHorizontalHeaderLabels(nomenclature_columns)

        row_count_table = 0
        for nomenclature in nomenclatures:
            characteristics = get_characteristic_for_good(self.session, nomenclature.id)
            if len(characteristics) == 0:
                characteristics = [""]
            for _ in characteristics:
                row_count_table += 1

        self.tableWidget_nomenclature.setRowCount(row_count_table)

        for nomenclature in nomenclatures:
            characteristics = get_characteristic_for_good(self.session, nomenclature.id)
            if len(characteristics) == 0:
                characteristics = [""]
            for characteristic in characteristics:

                article_item = QTableWidgetItem()
                article_item.setData(2, nomenclature.article)
                self.tableWidget_nomenclature.setItem(row_counter, 0, article_item)

                name_item = QTableWidgetItem()
                name_item.setData(2, nomenclature.name)
                name_item.setData(100, nomenclature.id)
                self.tableWidget_nomenclature.setItem(row_counter, 1, name_item)

                article_item = QTableWidgetItem()
                if characteristic == "":
                    article_item.setData(2, "")
                else:
                    article_item.setData(2, characteristic.name)
                    article_item.setData(100, characteristic.id)
                self.tableWidget_nomenclature.setItem(row_counter, 2, article_item)

                time_references_item = QTableWidgetItem()
                time_references_item.setData(2, nomenclature.time_references)
                self.tableWidget_nomenclature.setItem(row_counter, 3, time_references_item)
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
        self.get_all_nomenclature()


class CreateNomenclatureWidget(QtWidgets.QWidget, create_good.Ui_Form):
    def __init__(self):
        super().__init__()
        self.setupUi(self)


class CreateOrderWidget(QtWidgets.QWidget, create_order_widget.Ui_Form):
    def __init__(self):
        super().__init__()
        self.setupUi(self)


class CreateCharacteristicWidget(QtWidgets.QWidget, create_characteristic_widget.Ui_Form):
    def __init__(self):
        super().__init__()
        self.setupUi(self)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)  # Новый экземпляр QApplication
    window = MainWindow()  # Создаём объект класса ExampleApp
    window.show()  # Показываем окно
    app.exec_()  # и запускаем приложение
