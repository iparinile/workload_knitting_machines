import sys

from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QTableWidgetItem

import create_good

import create_order_widget
import create_characteristic_widget
import design
from queries import make_session, get_all_nomenclature, get_characteristic_for_good, create_nomenclature, \
    get_grouped_loading_of_machines, get_info_about_characteristic_in_order, get_order_by_one_c_id, create_order, \
    create_order_with_date_load, create_characteristic, get_all_characteristics_in_order, get_deadline_str_data, \
    get_all_orders


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
        self.fill_columns_to_filter()
        self.get_loading_of_machines()
        self.fill_orders_data()
        self.tabWidget.setCurrentIndex(0)
        self.lineEdit_filter.textChanged.connect(self.apply_filter)

    def fill_columns_to_filter(self):
        columns = ["Артикул", "Номенклатура", "Характеристика"]
        column_counter = 0
        for column_name in columns:
            self.comboBox_select_column.addItem(column_name, column_counter)
            column_counter += 1

    def apply_filter(self):
        column_index = self.comboBox_select_column.currentIndex()
        for row_number in range(self.tableWidget_nomenclature.rowCount()):
            cell_data = self.tableWidget_nomenclature.item(row_number, column_index).text().lower()
            filter_text = self.lineEdit_filter.text().lower()
            if filter_text is not None:
                if filter_text in cell_data:
                    self.tableWidget_nomenclature.showRow(row_number)
                else:
                    self.tableWidget_nomenclature.hideRow(row_number)
            else:
                self.tableWidget_nomenclature.showRow(row_number)

    def fill_orders_data(self):
        db_characteristics_in_order = get_all_characteristics_in_order(self.session)
        db_orders = get_all_orders(self.session)

        orders_columns = ["№ Заказа", "Артикул", "Номенклатура", "Характеристика", "Количество", "Дата окончания"]
        self.tableWidget_orders.setColumnCount(len(orders_columns))
        self.tableWidget_orders.setHorizontalHeaderLabels(orders_columns)

        row_count_table = len(db_characteristics_in_order) + len(db_orders)
        self.tableWidget_orders.setRowCount(row_count_table)

        row_counter = 0
        current_order_id = None
        current_deadline_date = None
        for current_characteristic_in_order in db_characteristics_in_order:
            characteristic_data = get_info_about_characteristic_in_order(
                self.session,
                current_characteristic_in_order.id
            )

            characteristic_data["deadline_date"] = get_deadline_str_data(
                self.session,
                current_characteristic_in_order.id
            )
            if characteristic_data["order_number"] != current_order_id:
                if current_order_id is not None:
                    order_number_item = QTableWidgetItem()
                    order_number_item.setData(2, current_order_id)
                    self.tableWidget_orders.setItem(row_counter, 0, order_number_item)

                    deadline_date_item = QTableWidgetItem()
                    deadline_date_item.setData(2, current_deadline_date)
                    self.tableWidget_orders.setItem(row_counter, 5, deadline_date_item)

                    current_order_id = characteristic_data["order_number"]
                    current_deadline_date = None
                    row_counter += 1
                else:
                    current_order_id = characteristic_data["order_number"]

            order_number_item = QTableWidgetItem()
            order_number_item.setData(2, characteristic_data["order_number"])
            self.tableWidget_orders.setItem(row_counter, 0, order_number_item)

            order_number_item = QTableWidgetItem()
            order_number_item.setData(2, characteristic_data["article"])
            self.tableWidget_orders.setItem(row_counter, 1, order_number_item)

            order_number_item = QTableWidgetItem()
            order_number_item.setData(2, characteristic_data["nomenclature_name"])
            self.tableWidget_orders.setItem(row_counter, 2, order_number_item)

            order_number_item = QTableWidgetItem()
            order_number_item.setData(2, characteristic_data["characteristic_name"])
            self.tableWidget_orders.setItem(row_counter, 3, order_number_item)

            order_number_item = QTableWidgetItem()
            order_number_item.setData(2, characteristic_data["amount"])
            self.tableWidget_orders.setItem(row_counter, 4, order_number_item)

            order_number_item = QTableWidgetItem()
            order_number_item.setData(2, characteristic_data["deadline_date"])
            self.tableWidget_orders.setItem(row_counter, 5, order_number_item)

            if current_deadline_date is None:
                current_deadline_date = characteristic_data["deadline_date"]
            elif characteristic_data["deadline_date"] > current_deadline_date:
                current_deadline_date = characteristic_data["deadline_date"]

            row_counter += 1

        order_number_item = QTableWidgetItem()
        order_number_item.setData(2, current_order_id)
        self.tableWidget_orders.setItem(row_counter, 0, order_number_item)

        deadline_date_item = QTableWidgetItem()
        deadline_date_item.setData(2, current_deadline_date)
        self.tableWidget_orders.setItem(row_counter, 5, deadline_date_item)
        self.tableWidget_orders.resizeColumnsToContents()

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
        self.fill_orders_data()

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

            machines_sheet.setRowCount(max_row_counter + 1)
            machines_sheet.setColumnCount(column_counter)

            column_headers = []
            for db_date_load in machine_load_data:
                column_headers.append(db_date_load['date'].strftime('%d.%m.%Y'))

            machines_sheet.setHorizontalHeaderLabels(column_headers)

            column_counter = 0
            for work_date_info in machine_load_data:
                total_load_item = QTableWidgetItem()
                total_load_item.setData(2, work_date_info['total_load'])
                machines_sheet.setItem(0, column_counter, total_load_item)
                row_counter = 1
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
        self.tableWidget_nomenclature.resizeColumnsToContents()

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
    # File = open("SyNet.qss", 'r')
    #
    # with File:
    #     qss = File.read()
    #     app.setStyleSheet(qss)
    window.show()  # Показываем окно
    app.exec_()  # и запускаем приложение
