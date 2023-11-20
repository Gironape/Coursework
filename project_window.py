import sys

import tools as tl
from PyQt5 import QtCore, QtWidgets
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
        self.scene = Scene()
        self.view = QGraphicsView(self.scene)
        self.setCentralWidget(self.view)
        self.view.mouseDoubleClickEvent = self.mouseDoubleClickEvent


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
        lamp = QAction(QIcon('lamp.png'), 'Lamp', self)
        wire = QAction(QIcon('wire.png'), 'Wire', self)

        self.toolbar = self.addToolBar('tools')
        self.toolbar.addAction(battery)
        self.toolbar.addAction(key)
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
        if btn.text() == "Lamp":
            lamp = QPixmap('Lamp.png')
            pixmap_item = QGraphicsPixmapItem(lamp.scaled(60, 60))
            pixmap_item.setFlag(QGraphicsItem.ItemIsMovable)
            self.scene.addItem(pixmap_item)
        elif btn.text() == "Key":
            key = QPixmap('Key.png')
            pixmap_item = QGraphicsPixmapItem(key.scaled(60, 60))
            pixmap_item.setFlag(QGraphicsItem.ItemIsMovable)
            self.scene.addItem(pixmap_item)
        elif btn.text() == "Battery":
            battery = QPixmap('Battery.png')
            pixmap_item = CustomItem(battery.scaled(60, 60))
            pixmap_item.setFlag(QGraphicsItem.ItemIsMovable)
            self.scene.addItem(pixmap_item)


class Scene(QtWidgets.QGraphicsScene):
    startItem = newConnection = None

    def controlPointAt(self, pos):
        mask = QPainterPath()
        mask.setFillRule(QtCore.Qt.WindingFill)
        for item in self.items(pos):
            if mask.contains(pos):
                # ignore objects hidden by others
                return
            if isinstance(item, ControlPoint):
                return item
            if not isinstance(item, ControlPoint):
                mask.addPath(item.shape().translated(item.scenePos()))

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            item = self.controlPointAt(event.scenePos())
            if item:
                self.startItem = item
                self.newConnection = Connection(item, event.scenePos())
                self.addItem(self.newConnection)
                return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.newConnection:
            item = self.controlPointAt(event.scenePos())
            if (item and item != self.startItem and
                self.startItem.onLeft != item.onLeft):
                    p2 = item.scenePos()
            else:
                p2 = event.scenePos()
            self.newConnection.setP2(p2)
            return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if self.newConnection:
            item = self.controlPointAt(event.scenePos())
            if item and item != self.startItem:
                self.newConnection.setEnd(item)
                if self.startItem.addLine(self.newConnection):
                    item.addLine(self.newConnection)
                else:
                    # delete the connection if it exists; remove the following
                    # line if this feature is not required
                    self.startItem.removeLine(self.newConnection)
                    self.removeItem(self.newConnection)
            else:
                self.removeItem(self.newConnection)
        self.startItem = self.newConnection = None
        super().mouseReleaseEvent(event)


class Connection(QtWidgets.QGraphicsLineItem):
    def __init__(self, start, p2):
        super().__init__()
        self.start = start
        self.end = None
        self._line = QtCore.QLineF(start.scenePos(), p2)
        self.setLine(self._line)

    def controlPoints(self):
        return self.start, self.end

    def setP2(self, p2):
        self._line.setP2(p2)
        self.setLine(self._line)

    def setStart(self, start):
        self.start = start
        self.updateLine()

    def setEnd(self, end):
        self.end = end
        self.updateLine(end)

    def updateLine(self, source):
        if source == self.start:
            self._line.setP1(source.scenePos())
        else:
            self._line.setP2(source.scenePos())
        self.setLine(self._line)


class ControlPoint(QtWidgets.QGraphicsEllipseItem):
    def __init__(self, parent, onLeft):
        super().__init__(-5, -5, 10, 10, parent)
        self.onLeft = onLeft
        self.lines = []
        # this flag **must** be set after creating self.lines!
        self.setFlags(self.ItemSendsScenePositionChanges)

    def addLine(self, lineItem):
        for existing in self.lines:
            if existing.controlPoints() == lineItem.controlPoints():
                # another line with the same control points already exists
                return False
        self.lines.append(lineItem)
        return True

    def removeLine(self, lineItem):
        for existing in self.lines:
            if existing.controlPoints() == lineItem.controlPoints():
                self.scene().removeItem(existing)
                self.lines.remove(existing)
                return True
        return False

    def itemChange(self, change, value):
        for line in self.lines:
            line.updateLine(self)
        return super().itemChange(change, value)


class CustomItem(QtWidgets.QGraphicsPixmapItem):
    def __init__(self, pixmap, left=True, right=True, parent=None):
        super().__init__(pixmap, parent)

        self.setFlags(self.ItemIsMovable)

        self.controls = []

        for onLeft, create in enumerate((right, left)):
            if onLeft == right:
                control = ControlPoint(self, onLeft)
                self.controls.append(control)
                control.setPen(QPen(QtCore.Qt.red, 2))
                control.setBrush(QBrush(QColor(214, 13, 36)))
                if onLeft:
                    control.setX(pixmap.width())
                control.setY(pixmap.height() / 2)
            else:
                control = ControlPoint(self, onLeft)
                self.controls.append(control)
                control.setPen(QPen(QtCore.Qt.blue, 2))
                control.setBrush(QBrush(QColor(00, 00, 255)))
                if onLeft:
                    control.setX(pixmap.width())
                control.setY(pixmap.height() / 2)


