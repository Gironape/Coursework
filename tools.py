from PyQt5.QtCore import QRectF, QLineF
from PyQt5.QtWidgets import *


class Lamp(QGraphicsItem):
    def __init__(self):
        super().__init__()

    def boundingRect(self):
        return QRectF(0, 0, 100, 100)

    def paint(self, painter, option, widget):
        painter.drawEllipse(0, 0, 100, 100)
        painter.drawLine(QLineF(100, 50, 150, 50))
        painter.drawLine(QLineF(-50, 50, 0, 50))
        painter.drawLine(QLineF(20, 10, 80, 90))
        painter.drawLine(QLineF(80, 10, 20, 90))


class Key(QGraphicsItem):
    def __init__(self):
        super().__init__()

    def boundingRect(self):
        return QRectF(0, 0, 150, 50)

    def paint(self, painter, option, widget):
        painter.drawLine(QLineF(0, 0, 50, 0))
        painter.drawLine(QLineF(50, 0, 100, -30))
        painter.drawLine(QLineF(100, 0, 150, 0))


class Battery(QGraphicsItem):
    def __init__(self):
        super().__init__()

    def boundingRect(self):
        return QRectF(0, 0, 125, 100)

    def paint(self, painter, option, widget):
        painter.drawLine(QLineF(50, 50, 100, 50))
        painter.drawLine(QLineF(100, 25, 100, 75))
        painter.drawLine(QLineF(125, 0, 125, 100))
        painter.drawLine(QLineF(125, 50, 175, 50))
        painter.drawLine(QLineF(75, 40, 90, 40))
        painter.drawLine(QLineF(130, 40, 145, 40))
        painter.drawLine(QLineF(137.5, 33, 137.5, 47))
