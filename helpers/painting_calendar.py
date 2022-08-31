from PyQt5 import QtWidgets, QtGui
from PyQt5.QtGui import QPainter


def my_paint_cell(self, painter, rect, date):
    QtWidgets.QCalendarWidget.paintCell(self, painter, rect, date)
    if date == self.date_to_paint:
        painter.setBrush(QtGui.QColor(0, 200, 200, 50))
        painter.drawRect(rect)
