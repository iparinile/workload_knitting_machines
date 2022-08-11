import sys

from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QTableWidgetItem, QComboBox, QMessageBox

import create_good
import create_order_form

import create_order_widget
import create_characteristic_widget
import design
from processing import delete_order_and_update_date_loads
from queries import make_session, get_all_nomenclature, get_characteristic_for_good, create_nomenclature, \
    get_grouped_loading_of_machines, get_info_about_characteristic_in_order, get_order_by_one_c_id, create_order, \
    create_date_load_to_characteristic, create_characteristic, get_all_characteristics_in_order, \
    get_deadline_for_characteristic_in_order, get_all_orders, get_characteristic_in_order, \
    create_characteristic_in_order, get_deadline_for_order, get_nomenclature_by_id, get_characteristics_for_order, \
    get_nomenclature_by_characteristic_id


class MainWindow(QtWidgets.QMainWindow, design.Ui_MainWindow):
    def __init__(self):
        self.create_good_widget = None
        self.create_characteristic_widget = None
        self.create_order_widget = None
        self.create_order_form = None
        self.new_good_data = None
        self.session = make_session()
        self.all_nomenclature = get_all_nomenclature(self.session)
        super().__init__()
        self.setupUi(self)  # Это нужно для инициализации нашего дизайна

        self.pushButton_add_good.clicked.connect(self.open_create_good_widget)
        self.pushButton_add_characteristic.clicked.connect(self.open_create_characteristic_widget)
        self.pushButton_add_order_to_select_nomenclature.clicked.connect(self.open_create_order_widget)
        self.pushButton_create_order.clicked.connect(self.open_create_order_form)
        self.pushButton_delete_selected_order.clicked.connect(self.delete_selected_order)

        self.tableWidget_orders.doubleClicked.connect(self.open_order_form)

        self.get_all_nomenclature()
        self.fill_columns_to_filter()
        self.get_loading_of_machines()
        self.fill_orders_data()
        self.tabWidget.setCurrentIndex(0)
        self.lineEdit_filter.textChanged.connect(self.apply_filter)

    def delete_selected_order(self):
        current_order_row_index = self.tableWidget_orders.currentRow()
        order_one_c_id = self.tableWidget_orders.item(current_order_row_index, 0).text()

        delete_order_and_update_date_loads(self.session, order_one_c_id)
        self.get_loading_of_machines()
        self.fill_orders_data()

    def open_order_form(self):
        self.all_nomenclature = get_all_nomenclature(self.session)
        self.create_order_form = CreateOrderForm()

        self.create_order_form.show()
        order_columns = ["Номенклатура", "Характеристика", "Количество", "Дата вязки"]
        self.create_order_form.tableWidget_characteristics_in_order.setColumnCount(len(order_columns))
        self.create_order_form.tableWidget_characteristics_in_order.setHorizontalHeaderLabels(order_columns)

        self.create_order_form.pushButton_add_row.clicked.connect(self.create_row_in_create_order_table)
        self.create_order_form.pushButton_delete_row.clicked.connect(self.delete_row_in_create_order_table)
        # self.create_order_form.pushButton_save.clicked.connect(self.create_order_from_form)

        current_order_row_index = self.tableWidget_orders.currentRow()
        order_one_c_id = self.tableWidget_orders.item(current_order_row_index, 0).text()

        self.create_order_form.lineEdit_order_one_c_id.setText(order_one_c_id)
        self.create_order_form.lineEdit_order_one_c_id.setEnabled(False)

        order_one_c_id = int(order_one_c_id)
        self.fill_order_form(order_one_c_id)

    def open_create_order_form(self):
        self.all_nomenclature = get_all_nomenclature(self.session)
        self.create_order_form = CreateOrderForm()

        self.create_order_form.show()
        order_columns = ["Номенклатура", "Характеристика", "Количество", "Дата вязки"]
        self.create_order_form.tableWidget_characteristics_in_order.setColumnCount(len(order_columns))
        self.create_order_form.tableWidget_characteristics_in_order.setHorizontalHeaderLabels(order_columns)

        self.create_order_form.pushButton_add_row.clicked.connect(self.create_row_in_create_order_table)
        self.create_order_form.pushButton_delete_row.clicked.connect(self.delete_row_in_create_order_table)
        self.create_order_form.pushButton_save.clicked.connect(self.create_order_from_form)

        self.create_row_in_create_order_table()

        self.create_order_form.tableWidget_characteristics_in_order.resizeColumnsToContents()

    def create_order_from_form(self):
        table_with_characteristic = self.create_order_form.tableWidget_characteristics_in_order
        order_one_c_id = self.create_order_form.lineEdit_order_one_c_id.text()

        if order_one_c_id == '':
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText("Ошибка")
            msg.setInformativeText('Не указан номер заказа')
            msg.setWindowTitle("Ошибка")
            msg.exec_()
        else:
            db_order = get_order_by_one_c_id(self.session, order_one_c_id)

            if db_order is None:
                db_order = create_order(self.session, order_one_c_id)

            for row_counter in range(table_with_characteristic.rowCount()):
                # article_combobox: QComboBox = table_with_characteristic.cellWidget(row_counter, 0)
                # nomenclature_id = article_combobox.itemData(article_combobox.currentIndex())
                #
                # article = table_with_characteristic.item(row_counter, 1).text()

                characteristic_combobox: QComboBox = table_with_characteristic.cellWidget(row_counter, 1)
                characteristic_id = characteristic_combobox.itemData(characteristic_combobox.currentIndex())

                amount = int(table_with_characteristic.item(row_counter, 2).text())
                db_characteristic_in_order = get_characteristic_in_order(self.session, db_order.id, characteristic_id)

                if db_characteristic_in_order is not None:
                    pass
                else:
                    db_characteristic_in_order = create_characteristic_in_order(
                        self.session,
                        db_order.id,
                        characteristic_id,
                        amount
                    )

                create_date_load_to_characteristic(
                    self.session,
                    db_characteristic_in_order,
                    characteristic_id,
                    amount
                )
            self.fill_order_form(order_one_c_id)
            self.fill_orders_data()
            self.get_loading_of_machines()

    def fill_order_form(self, order_one_c_id: int):
        db_order = get_order_by_one_c_id(self.session, order_one_c_id)
        self.create_order_form.lineEdit_order_one_c_id.text = order_one_c_id
        order_columns = ["Номенклатура", "Характеристика", "Количество", "Дата вязки"]
        self.create_order_form.tableWidget_characteristics_in_order.setColumnCount(len(order_columns))
        self.create_order_form.tableWidget_characteristics_in_order.setHorizontalHeaderLabels(order_columns)

        db_characteristics_for_order = get_characteristics_for_order(self.session, db_order.id)
        self.create_order_form.tableWidget_characteristics_in_order.setRowCount(len(db_characteristics_for_order))

        row_counter = 0
        for current_characteristic in db_characteristics_for_order:
            characteristic_info = get_info_about_characteristic_in_order(
                self.session,
                current_characteristic.id
            )
            select_article_combobox = QComboBox()
            select_article_combobox.setEditable(True)
            for nomenclature in self.all_nomenclature:
                select_article_combobox.addItem(nomenclature.name, nomenclature.id)
            article_index = select_article_combobox.findText(characteristic_info["nomenclature_name"])
            select_article_combobox.setCurrentIndex(article_index)

            self.create_order_form.tableWidget_characteristics_in_order.setCellWidget(
                row_counter,
                0,
                select_article_combobox
            )

            db_nomenclature = get_nomenclature_by_characteristic_id(
                self.session,
                current_characteristic.characteristic_id
            )
            db_characteristics = get_characteristic_for_good(self.session, db_nomenclature.id)

            select_characteristic_combobox = QComboBox()
            select_characteristic_combobox.setEditable(True)

            for characteristic in db_characteristics:
                select_characteristic_combobox.addItem(characteristic.name, characteristic.id)
            characteristic_index = select_characteristic_combobox.findData(current_characteristic.characteristic_id)
            select_characteristic_combobox.setCurrentIndex(characteristic_index)

            self.create_order_form.tableWidget_characteristics_in_order.setCellWidget(
                row_counter,
                1,
                select_characteristic_combobox
            )
            amount_item = QTableWidgetItem()
            amount_item.setData(2, characteristic_info["amount"])
            self.create_order_form.tableWidget_characteristics_in_order.setItem(
                row_counter,
                2,
                amount_item
            )

            deadline = get_deadline_for_characteristic_in_order(self.session, current_characteristic.id)
            deadline_item = QTableWidgetItem()
            deadline_item.setData(2, deadline.strftime("%d.%m.%y"))
            self.create_order_form.tableWidget_characteristics_in_order.setItem(
                row_counter,
                3,
                deadline_item
            )

            row_counter += 1
        self.create_order_form.tableWidget_characteristics_in_order.resizeColumnsToContents()

    def delete_row_in_create_order_table(self):
        row_count = self.create_order_form.tableWidget_characteristics_in_order.currentRow()
        self.create_order_form.tableWidget_characteristics_in_order.removeRow(row_count)

    def create_row_in_create_order_table(self):
        row_count = self.create_order_form.tableWidget_characteristics_in_order.rowCount()
        self.create_order_form.tableWidget_characteristics_in_order.insertRow(row_count)
        new_row_index = row_count
        select_article_combobox = QComboBox()
        select_article_combobox.setEditable(True)

        for nomenclature in self.all_nomenclature:
            select_article_combobox.addItem(nomenclature.name, nomenclature.id)
        select_article_combobox.setCurrentIndex(-1)

        self.create_order_form.tableWidget_characteristics_in_order.setCellWidget(
            new_row_index,
            0,
            select_article_combobox
        )
        select_article_combobox.currentIndexChanged.connect(self.fill_data_about_characteristics_to_nomenclature)

    def fill_data_about_characteristics_to_nomenclature(self):
        combobox = self.sender()
        current_row = self.create_order_form.tableWidget_characteristics_in_order.currentRow()
        nomenclature_id = combobox.itemData(combobox.currentIndex())
        db_nomenclature = get_nomenclature_by_id(self.session, nomenclature_id)
        db_characteristics = get_characteristic_for_good(self.session, nomenclature_id)

        select_characteristic_combobox = QComboBox()
        select_characteristic_combobox.setEditable(True)

        for characteristic in db_characteristics:
            select_characteristic_combobox.addItem(characteristic.name, characteristic.id)
        select_characteristic_combobox.setCurrentIndex(-1)

        self.create_order_form.tableWidget_characteristics_in_order.setCellWidget(
            current_row,
            1,
            select_characteristic_combobox
        )
        self.create_order_form.tableWidget_characteristics_in_order.resizeColumnsToContents()

    def fill_columns_to_filter(self):
        columns = ["Номенклатура", "Характеристика"]
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
        db_orders = get_all_orders(self.session)

        orders_columns = ["№ Заказа", "Дата вязки"]
        self.tableWidget_orders.setColumnCount(len(orders_columns))
        self.tableWidget_orders.setHorizontalHeaderLabels(orders_columns)

        row_count_table = len(db_orders)
        self.tableWidget_orders.setRowCount(row_count_table)

        row_counter = 0
        for order in db_orders:
            order_deadline = get_deadline_for_order(self.session, order.id)

            order_id_item = QTableWidgetItem()
            order_id_item.setData(2, order.one_c_id)
            self.tableWidget_orders.setItem(row_counter, 0, order_id_item)

            deadline_order_item = QTableWidgetItem()
            deadline_order_item.setData(2, order_deadline.strftime("%d.%m.%y"))
            self.tableWidget_orders.setItem(row_counter, 1, deadline_order_item)

            row_counter += 1

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

        db_characteristic_in_order = get_characteristic_in_order(self.session, db_order.id, characteristic_id)

        if db_characteristic_in_order is not None:
            pass
        else:
            db_characteristic_in_order = create_characteristic_in_order(
                self.session,
                db_order.id,
                characteristic_id,
                characteristic_amount
            )

        create_date_load_to_characteristic(
            self.session,
            db_characteristic_in_order,
            characteristic_id,
            characteristic_amount
        )
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
        nomenclature_columns = ["Номенклатура", "Характеристика", "Время изготовления, мин."]
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
                article_item.setData(2, nomenclature.name)
                self.tableWidget_nomenclature.setItem(row_counter, 0, article_item)

                article_item = QTableWidgetItem()
                if characteristic == "":
                    article_item.setData(2, "")
                else:
                    article_item.setData(2, characteristic.name)
                    article_item.setData(100, characteristic.id)
                self.tableWidget_nomenclature.setItem(row_counter, 1, article_item)

                time_references_item = QTableWidgetItem()
                time_references_item.setData(2, nomenclature.time_references)
                self.tableWidget_nomenclature.setItem(row_counter, 2, time_references_item)
                row_counter += 1
        self.tableWidget_nomenclature.resizeColumnsToContents()

    def open_create_good_widget(self):
        self.create_good_widget = CreateNomenclatureWidget()

        self.create_good_widget.show()

        self.create_good_widget.pushButton_save.clicked.connect(self.create_good)

    def create_good(self):
        self.new_good_data = {
            "name": self.create_good_widget.lineEdit_name.text(),
            "time_references": self.create_good_widget.lineEdit_time_references.text()
        }

        create_nomenclature(
            session=self.session,
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


class CreateOrderForm(QtWidgets.QWidget, create_order_form.Ui_Form_order):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
    #
    # def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
    #     print("test")


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
