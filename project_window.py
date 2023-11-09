import sys

from PyQt5 import QtCore
from PyQt5.QtCore import QSize
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *


class Project(QMainWindow):
    def __init__(self):
        super(Project, self).__init__()
        self.toolbar = None
        self.buttons()
        self.ext = None
        self.btn_exit = None
        self.menuBar = None
        self.setWindowIcon(QIcon('Tape2.jpg'))
        self.setFont(QFont('Arial', 20))
        self.setStyleSheet("background-color:;")
        self.setWindowTitle("VCP")
        self.setGeometry(0, 0, 1920, 1080)
        self.create_menu_bar()
        self.create_tool_bar()

    def buttons(self):
        self.btn_exit = QPushButton(self)
        self.btn_exit.setGeometry(150, 200, 300, 30)
        self.btn_exit.setText("Выход")
        self.btn_exit.setShortcut("Escape")
        self.btn_exit.clicked.connect(self.exit)

    def exit(self):
        ext = QMessageBox()
        ext.setWindowTitle("Выход")
        ext.setText("Вы действительно хотите выйти?")
        ext.setIcon(QMessageBox.Question)
        ext.setWindowIcon(QIcon('Tape2.jpg'))
        ext.setStandardButtons(QMessageBox.Save | QMessageBox.Yes | QMessageBox.No)
        ext.setInformativeText("Сохраните проект перед выходом")
        ext.buttonClicked.connect(self.press)
        ext.exec_()

    def press(self, btn):
        if btn.text() == "Yes":
            sys.exit()
        elif btn.text() == "Save":
            file = QFileDialog.getSaveFileName(self)[0]
            try:
                f = open(file, 'r')
                f.write(file)
            except FileNotFoundError:
                print("No such file")

    def create_menu_bar(self):
        self.menuBar = QMenuBar(self)
        self.setMenuBar(self.menuBar)

        fileMenu = QMenu("&File", self)
        self.menuBar.addMenu(fileMenu)

        fileMenu.addAction('Open', self.action_clicked)
        fileMenu.addAction('Save', self.action_clicked)
        fileMenu.addAction('Save As', self.action_clicked)

    def create_tool_bar(self):
        battery = QAction(QIcon('battery.png'), 'Battery', self)
        # tools.setShortcut('Ctrl+Q') Нужно для понимания
        # tools.triggered.connect(qApp.quit)
        key = QAction(QIcon('key.png'), 'Key', self)
        resistor = QAction(QIcon('resistor.png'), 'Resistor', self)
        lamp = QAction(QIcon('lamp.png'), 'Lamp', self)
        wire = QAction(QIcon('wire.png'), 'Wire', self)

        self.toolbar = self.addToolBar('tools')
        self.toolbar.addAction(battery)
        self.toolbar.addAction(key)
        self.toolbar.addAction(resistor)
        self.toolbar.addAction(lamp)
        self.toolbar.addAction(wire)
        self.toolbar.setFixedHeight(100)
        self.toolbar.setIconSize(QSize(50, 50))

    @QtCore.pyqtSlot()
    def action_clicked(self):
        action = self.sender()
        print("Action: " + action.text())
