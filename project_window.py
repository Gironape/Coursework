import pickle
import sys
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

    # РАЗОБРАТЬСЯ С СОХРАНЕНИЕМ

    def save_project(self):
        file_name, _ = QFileDialog.getSaveFileName(self, "Save Project", "", "Project Files (*.proj);;All Files (*)")
        if file_name:
            with open(file_name, 'wb') as f:
                for item in self.scene.items():
                    pickle.dump(item, f)
            f.close()

    def create_tool_bar(self):
        battery = QAction(QIcon('Tools/battery.png'), 'Battery', self)
        # tools.setShortcut('Ctrl+Q') Нужно для понимания
        # tools.triggered.connect(qApp.quit)
        key = QAction(QIcon('Tools/key.png'), 'Key', self)
        lamp = QAction(QIcon('Tools/lamp_off.png'), 'Lamp', self)
        self.start_stop = QAction(QIcon('Tools/start.png'), 'Start/Stop', self)
        fan = QAction(QIcon('Tools/fan.gif'), 'Fan', self)
        accumulator = QAction(QIcon('Tools/accumulator.png'), 'Accumulator', self)

        self.toolbar = self.addToolBar('tools')
        self.toolbar.addAction(battery)
        self.toolbar.addAction(key)
        self.toolbar.addAction(lamp)
        self.toolbar.addAction(accumulator)
        self.toolbar.addAction(fan)
        separator = QLabel('', self)
        separator.setFixedWidth(700)  # Устанавливаем фиксированную ширину разделителя
        self.toolbar.addWidget(separator)
        self.toolbar.addAction(self.start_stop)
        self.toolbar.setFixedHeight(100)
        self.toolbar.setIconSize(QSize(50, 50))

        self.toolbar.actionTriggered.connect(self.tool_bar_clicked)

    @QtCore.pyqtSlot()
    def menu_bar_clicked(self):
        action = self.sender()
        if action.text() == "Save":
            self.save_project()
        elif action.tex() == "Open":
            pass

    def tool_bar_clicked(self, btn):
        if btn.text() == "Lamp":
            lamp = QPixmap('Tools/Lamp_off.png')
            lamp_item = Lamp(lamp.scaled(60, 60))
            self.scene.addItem(lamp_item)
        elif btn.text() == "Key":
            key = QPixmap('Tools/Key.png')
            key_item = Key(key.scaled(60, 60))
            self.scene.addItem(key_item)
        elif btn.text() == "Battery":
            battery = QPixmap('Tools/Battery.png')
            battery_item = Battery(battery.scaled(60, 60))
            self.scene.addItem(battery_item)
        elif btn.text() == "Start/Stop":
            if self.start_stop.property("state") is None or self.start_stop.property("state") == "on":
                self.start_stop.setIcon(QIcon('Tools/stop.png'))
                self.start_stop.setProperty("state", "off")
                include(self.scene, on=False)
            else:
                self.start_stop.setIcon(QIcon('Tools/start.png'))
                self.start_stop.setProperty("state", "on")
                include(self.scene, on=True)
                print("Stop")
        elif btn.text() == "Fan":
            fan = QPixmap('Tools/fan.gif')
            self.fan_item = Fan(fan.scaled(60, 60), gif_path='Tools/fan.gif')
            self.scene.addItem(self.fan_item)
        elif btn.text() == "Accumulator":
            accumulator = QPixmap('Tools/accumulator.png')
            accumulator_item = Accumulator(accumulator.scaled(70, 60))
            self.scene.addItem(accumulator_item)


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
                    print("BAZAR", self.newConnection.add_connection())
                else:
                    # delete the connection if it exists; remove the following
                    # line if this feature is not required
                    print("VOKZAL", self.newConnection.delete_connection())
                    item.removeLine(self.newConnection)
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

    def add_connection(self):
        for item in self.scene().items():
            if isinstance(item, CustomItem):
                if item.connect_plus == self.start:
                    for item2 in self.scene().items():
                        if isinstance(item2, CustomItem):
                            if item2.connect_minus == self.end:
                                item.wire_connection_plus.append(item2.name)
                                item2.wire_connection_minus.append(item.name)
                                return item, item.wire_connection_plus, item.wire_connection_minus, item2, item2.wire_connection_plus, item2.wire_connection_minus
                elif item.connect_minus == self.start:
                    for item2 in self.scene().items():
                        if isinstance(item2, CustomItem):
                            if item2.connect_plus == self.end:
                                item.wire_connection_minus.append(item2.name)
                                item2.wire_connection_plus.append(item.name)
                                return item, item.wire_connection_plus, item.wire_connection_minus, item2, item2.wire_connection_plus, item2.wire_connection_minus

    def delete_connection(self):
        for item in self.scene().items():
            if isinstance(item, CustomItem):
                if item.connect_plus == self.start:
                    for item2 in self.scene().items():
                        if isinstance(item2, CustomItem):
                            if item2.connect_minus == self.end:
                                item.wire_connection_plus.remove(item2.name)
                                item2.wire_connection_minus.remove(item.name)
                                return item, item.wire_connection_plus, item.wire_connection_minus, item2, item2.wire_connection_plus, item2.wire_connection_minus
                elif item.connect_minus == self.start:
                    for item2 in self.scene().items():
                        if isinstance(item2, CustomItem):
                            if item2.connect_plus == self.end:
                                item.wire_connection_minus.remove(item2.name)
                                item2.wire_connection_plus.remove(item.name)
                                return item, item.wire_connection_plus, item.wire_connection_minus, item2, item2.wire_connection_plus, item2.wire_connection_minus


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
    def __init__(self, pixmap, minus=True, plus=True, parent=None):
        super().__init__(pixmap, parent)

        self.connect_minus = None
        self.connect_plus = None
        self.setFlags(self.ItemIsMovable)
        self.name = "None"
        self.wire_connection_plus = []
        self.wire_connection_minus = []
        self.create(minus, plus, pixmap)

    def create(self, minus, plus, pixmap):
        for onLeft, create in enumerate((minus, plus)):
            if create:
                control = ControlPoint(self, onLeft)
                if onLeft == plus:
                    control.setPen(QPen(QtCore.Qt.red, 1))
                    control.setBrush(QBrush(QColor(214, 13, 36)))
                    self.connect_plus = control
                else:
                    control.setPen(QPen(QtCore.Qt.blue, 1))
                    control.setBrush(QBrush(QColor(0, 0, 255)))
                    self.connect_minus = control
                if onLeft:
                    control.setX(pixmap.width())
                control.setY(pixmap.height() / 2)


class Battery(CustomItem):

    def __init__(self, pixmap, minus=True, plus=True, parent=None):
        super().__init__(pixmap, minus, plus, parent)
        self.name = "Battery"


class Lamp(CustomItem):
    def __init__(self, pixmap, minus=True, plus=True, parent=None):
        super().__init__(pixmap, minus, plus, parent)

        self.name = "Lamp"


class Key(CustomItem):
    def __init__(self, pixmap, minus=True, plus=True, parent=None):
        super().__init__(pixmap, minus, plus, parent)

        self.name = "Key"


class Accumulator(CustomItem):

    def __init__(self, pixmap, minus=True, plus=True, parent=None):
        super().__init__(pixmap, minus, plus, parent)

        self.name = "Accumulator"

    def create(self, minus, plus, pixmap):
        super().create(minus=True, plus=True, pixmap=pixmap)
        self.connect_minus.setY(pixmap.height() / 12)
        self.connect_minus.setX(pixmap.width() / 6)
        self.connect_plus.setY(pixmap.height() / 12)
        self.connect_plus.setX(pixmap.width() / 1.23)


class Fan(CustomItem):
    def __init__(self, pixmap, minus=True, plus=True, parent=None, gif_path=""):
        super().__init__(pixmap, minus, plus, parent)

        self.name = "Fan"
        self.gif_movie = QMovie(gif_path) if gif_path else None
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_pixmap)
        self.pixmap_number = 0
        self.lvl = 1

    def update_pixmap(self):
        if self.gif_movie:
            self.gif_movie.jumpToFrame(self.pixmap_number)
            self.setPixmap(self.gif_movie.currentPixmap())
            self.pixmap_number += 1
            if self.pixmap_number >= self.gif_movie.frameCount():
                self.pixmap_number = 0

    def start(self):
        if self.lvl == 1:
            self.timer.start(200)
        if self.lvl == 2:
            self.timer.start(100)
        if self.lvl == 3:
            self.timer.start(50)

    def stop(self):
        self.timer.stop()

    def level(self, item):
        if "Battery" in item.wire_connection_plus and "Battery" in item.wire_connection_minus:
            self.lvl = 3
        else:
            self.lvl = 1


def include(scene, on):
    if not on:
        for item in scene.items():
            if isinstance(item, Lamp):
                if "Battery" or "Accumulator" in item.wire_connection_plus and "Battery" or "Accumulator" or "Key" in \
                        item.wire_connection_minus:
                    item.setPixmap(QPixmap('Tools/lamp_on.png').scaled(60, 60))
            if isinstance(item, Fan):
                if "Battery" or "Accumulator" in item.wire_connection_plus and "Battery" or "Accumulator" or "Key" in \
                        item.wire_connection_minus:
                    item.level(item)
                    item.start()
    elif on:
        for item in scene.items():
            if isinstance(item, Lamp):
                item.setPixmap(QPixmap('Tools/lamp_off.png').scaled(60, 60))
            if isinstance(item, Fan):
                item.stop()
