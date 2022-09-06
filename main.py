import sys
from datetime import date

from PyQt5 import QtWidgets
from PyQt5.QtCore import QDate, QTranslator
from PyQt5.QtWidgets import QTableWidgetItem, QComboBox, QMessageBox, QTextBrowser

from Interfaces import create_characteristic_widget, design, create_good, create_order_form, create_order_widget
from helpers.create_critical_message_box import create_message_box

from helpers.painting_calendar import my_paint_cell
from processing import delete_order_and_update_date_loads
from queries.date_loads import get_date_load_for_knitting_machine, get_date_load_for_machine_on_date
from queries.knitting_machines import get_all_knitting_machines
from queries.session import make_session
from queries.load_knitting_machines import create_date_load_to_characteristic, \
    get_deadline_for_characteristic_in_order, get_load_machine_by_date_load, get_load_knitting_machines_by_date_load_id
from queries.characteristic_in_order import create_characteristic_in_order, get_info_about_characteristic_in_order, \
    get_characteristics_for_order, get_characteristic_in_order
from queries.orders import create_order, get_order_by_one_c_id, get_all_orders, get_deadline_for_order
from queries.characteristic import get_characteristic_for_good, create_characteristic
from queries.nomenclature import create_nomenclature, get_all_nomenclature, get_nomenclature_by_characteristic_id


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

        self.calendarWidget_5_grade.clicked.connect(
            lambda: self.fill_load_machine_data_on_form(1, self.calendarWidget_5_grade.selectedDate(),
                                                        self.textBrowser_5_grade))
        self.calendarWidget_7_grade.clicked.connect(
            lambda: self.fill_load_machine_data_on_form(2, self.calendarWidget_7_grade.selectedDate(),
                                                        self.textBrowser_7_grade))
        self.calendarWidget_10_grade.clicked.connect(
            lambda: self.fill_load_machine_data_on_form(1, self.calendarWidget_10_grade.selectedDate(),
                                                        self.textBrowser_10_grade))
        self.calendarWidget_12_grade.clicked.connect(
            lambda: self.fill_load_machine_data_on_form(1, self.calendarWidget_12_grade.selectedDate(),
                                                        self.textBrowser_12_grade))
        self.calendarWidget_12_1_grade.clicked.connect(
            lambda: self.fill_load_machine_data_on_form(1, self.calendarWidget_12_1_grade.selectedDate(),
                                                        self.textBrowser_12_1_grade))

        self.tableWidget_orders.doubleClicked.connect(self.open_order_form)

        self.get_all_nomenclature()
        self.fill_columns_to_filter()
        self.get_loading_of_machines()
        self.fill_orders_data()
        self.tabWidget.setCurrentIndex(0)
        self.lineEdit_filter.textChanged.connect(self.apply_filter)

    def fill_load_machine_data_on_form(self, machine_id: int, selected_date: QDate, text_browser: QTextBrowser):
        date_load = get_date_load_for_machine_on_date(self.session, machine_id, selected_date.toPyDate())
        if date_load is not None:
            load_text_to_widget = ""
            today_loads_machine = get_load_knitting_machines_by_date_load_id(self.session, date_load.id)
            if len(today_loads_machine) > 0:
                for load_machine in today_loads_machine:
                    characteristic_info = get_info_about_characteristic_in_order(
                        self.session,
                        load_machine.characteristic_in_order_id
                    )
                    load_info = f"Заказ {characteristic_info['order_number']}, " \
                                f"{characteristic_info['nomenclature_name']}, " \
                                f"{characteristic_info['characteristic_name']}, " \
                                f"время - {load_machine.time_references} минут"
                    load_text_to_widget += load_info
                    load_text_to_widget += "\n"
            text_browser.setText(load_text_to_widget)

    def delete_selected_order(self):
        message_box = QMessageBox.question(self, "Удаление заказа", "Вы точно хотите удалить заказ?",
                                           defaultButton=QMessageBox.No)
        if message_box == QMessageBox.Yes:
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
            create_message_box("Не указан номер заказа")
        else:
            if table_with_characteristic.rowCount() == 0:
                create_message_box("Не указаны товары")
            else:
                db_order = get_order_by_one_c_id(self.session, order_one_c_id)

                if db_order is None:
                    db_order = create_order(self.session, order_one_c_id)

                for row_counter in range(table_with_characteristic.rowCount()):

                    characteristic_combobox: QComboBox = table_with_characteristic.cellWidget(row_counter, 1)
                    characteristic_id = characteristic_combobox.itemData(characteristic_combobox.currentIndex())

                    amount = int(table_with_characteristic.item(row_counter, 2).text())
                    db_characteristic_in_order = get_characteristic_in_order(self.session, db_order.id,
                                                                             characteristic_id)

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
        knitting_machines = get_all_knitting_machines(self.session)
        for db_knitting_machine in knitting_machines:
            machines_id = db_knitting_machine.id
            machines_calendar = self.calendarWidget_5_grade  # Придумать заглушку
            text_browser = self.textBrowser_5_grade
            if machines_id == 1:
                machines_calendar = self.calendarWidget_5_grade
                text_browser = self.textBrowser_5_grade
            elif machines_id == 2:
                machines_calendar = self.calendarWidget_7_grade
                text_browser = self.textBrowser_7_grade
            elif machines_id == 3:
                machines_calendar = self.calendarWidget_10_grade
                text_browser = self.textBrowser_10_grade
            elif machines_id == 4:
                machines_calendar = self.calendarWidget_12_grade
                text_browser = self.textBrowser_12_grade
            elif machines_id == 5:
                machines_calendar = self.calendarWidget_12_1_grade
                text_browser = self.textBrowser_12_1_grade

            machines_calendar.dates_to_paint = []
            date_loads_for_machine = get_date_load_for_knitting_machine(self.session, machines_id)
            for db_date_load in date_loads_for_machine:
                if get_load_machine_by_date_load(self.session, db_date_load.id) is not None:
                    date_obj: date = db_date_load.date
                    machines_calendar.dates_to_paint.append(QDate(date_obj.year, date_obj.month, date_obj.day))

            machines_calendar.paintCell = my_paint_cell.__get__(machines_calendar, MainWindow)

            today_date_load = get_date_load_for_machine_on_date(self.session, machines_id, date.today())
            if today_date_load is not None:
                today_loads_machine = get_load_knitting_machines_by_date_load_id(self.session, today_date_load.id)
                if len(today_loads_machine) > 0:
                    info_to_widget = ""
                    for load_machine in today_loads_machine:
                        characteristic_info = get_info_about_characteristic_in_order(
                            self.session,
                            load_machine.characteristic_in_order_id
                        )
                        load_info = f"Заказ {characteristic_info['order_number']}, " \
                                    f"{characteristic_info['nomenclature_name']}, " \
                                    f"{characteristic_info['characteristic_name']}, " \
                                    f"время - {load_machine.time_references} минут"
                        info_to_widget += load_info
                        info_to_widget += "\n"

                    text_browser.setText(info_to_widget)

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
    translator = QTranslator(app)
    translator.load("qtbase_ru.qm")
    app.installTranslator(translator)
    # File = open("SyNet.qss", 'r')
    #
    # with File:
    #     qss = File.read()
    #     app.setStyleSheet(qss)
    window.show()  # Показываем окно
    app.exec_()  # и запускаем приложение
