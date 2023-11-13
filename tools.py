import sys

from PyQt5 import QtCore
from PyQt5.QtCore import QSize
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *


class Tools(QWidget):
    def __init__(self):
        super(Tools, self).__init__()
        self.setGeometry(500, 200, 100, 100)
        self.v = None
        self.battery()

    def battery(self):
        self.v = QLabel(self)
        self.v.setText("Напряжение 220В")
        self.show()
