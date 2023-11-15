import random
import sys

from PyQt5.QtPrintSupport import QPrinter

import tools as tl
from PyQt5 import QtCore
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *


class Project(QMainWindow):
    def __init__(self):
        super(Project, self).__init__()
        self.toolbar = QToolBar("My main toolbar")
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
        self.setAcceptDrops(True)
        self.scene = QGraphicsScene(self)
        self.view = QGraphicsView(self.scene)
        self.setCentralWidget(self.view)
        self.item = QGraphicsItem()

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
                f = open(file, 'w')
                f.write(file)
            except FileNotFoundError:
                print("No such file")

    def create_menu_bar(self):
        self.menuBar = QMenuBar(self)
        self.setMenuBar(self.menuBar)

        fileMenu = QMenu("&File", self)
        self.menuBar.addMenu(fileMenu)

        fileMenu.addAction('Open', self.menu_bar_clicked)
        fileMenu.addAction('Save', self.menu_bar_clicked)
        fileMenu.addAction('Save As', self.menu_bar_clicked)

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
        self.toolbar.actionTriggered.connect(self.tool_bar_clicked)

    @QtCore.pyqtSlot()
    def menu_bar_clicked(self):
        action = self.sender()
        print("Action: " + action.text())

    def tool_bar_clicked(self, btn):
        if btn.text() == "Resistor":
            resistor = self.scene.addRect(50, 50, 100, 50)
            resistor = self.scene.addLine(150, 75, 200, 75)
            resistor = self.scene.addLine(0, 75, 50, 75)
            self.scene.addItem(resistor)
        elif btn.text() == "Lamp":
            lamp = self.scene.addEllipse(0, 0, 100, 100)
            lamp = self.scene.addLine(100, 50, 150, 50)
            lamp = self.scene.addLine(-50, 50, 0, 50)
            lamp = self.scene.addLine(20, 10, 80, 90)
            lamp = self.scene.addLine(80, 10, 20, 90)
            self.scene.addItem(lamp)
        elif btn.text() == "Key":
            key = self.scene.addLine(50, 50, 100, 50)
            key = self.scene.addLine(100, 50, 150, 20)
            key = self.scene.addLine(150, 50, 200, 50)
            self.scene.addItem(key)
        elif btn.text() == "Battery":
            battery = self.scene.addLine(50, 50, 100, 50)
            battery = self.scene.addLine(100, 25, 100, 75)
            battery = self.scene.addLine(125, 0, 125, 100)
            battery = self.scene.addLine(125, 50, 175, 50)
            battery = self.scene.addLine(75, 40, 90, 40)
            battery = self.scene.addLine(130, 40, 145, 40)
            battery = self.scene.addLine(137.5, 33, 137.5, 47)
            self.scene.addItem(battery)


