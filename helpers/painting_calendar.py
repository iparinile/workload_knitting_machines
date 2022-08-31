from PyQt5 import QtWidgets, QtGui


def my_paint_cell(self, painter, rect, date):
    QtWidgets.QCalendarWidget.paintCell(self, painter, rect, date)
    if date in self.dates_to_paint:
        painter.setBrush(QtGui.QColor(255, 120, 120, 100))
        painter.setPen(QtGui.QColor(0, 0, 0, 0))
        painter.drawRect(rect)
