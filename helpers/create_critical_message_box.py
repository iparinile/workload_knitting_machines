from PyQt5.QtWidgets import QMessageBox


def create_message_box(message_text: str) -> None:
    message_box = QMessageBox()
    message_box.setIcon(QMessageBox.Critical)
    message_box.setText("Ошибка")
    message_box.setInformativeText(message_text)
    message_box.setWindowTitle("Ошибка")
    message_box.exec_()
