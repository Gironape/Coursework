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
        self.for_redo = []

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
            pass

    def create_menu_bar(self):
        self.menuBar = QMenuBar(self)
        self.setMenuBar(self.menuBar)

        fileMenu = QMenu("&File", self)
        self.menuBar.addMenu(fileMenu)
        open_file = QAction('Open', self)
        open_file.setIcon(QIcon('Menu/open.png'))
        save_file = QAction('Save', self)
        save_file.setIcon(QIcon('Menu/save.png'))
        save_file_as = QAction('Save as', self)
        fileMenu.addAction(open_file)
        fileMenu.addAction(save_file)
        fileMenu.addAction(save_file_as)
        fileMenu.triggered[QAction].connect(self.menu_bar_clicked)

        editMenu = QMenu("&Edit", self)
        self.menuBar.addMenu(editMenu)
        undo = QAction('Undo', self)
        undo.setIcon(QIcon('Menu/undo.png'))
        undo.setShortcut(QKeySequence.Undo)
        redo = QAction('Redo', self)
        redo.setIcon(QIcon('Menu/redo.png'))
        redo.setShortcut('Ctrl+Shift+Z')
        editMenu.addAction(undo)
        editMenu.addAction(redo)
        editMenu.triggered[QAction].connect(self.menu_bar_clicked)

        # РАЗОБРАТЬСЯ С СОХРАНЕНИЕМ

    def save_file(self):
        items_data = []
        for item in self.scene.items():
            if isinstance(item, CustomItem):
                item_data = {
                    'type': type(item).__name__,
                    'pos': (item.scenePos().x(), item.scenePos().y()),
                    'connect_minus': item.wire_connection_minus,
                    'connect_plus': item.wire_connection_plus
                }
                items_data.append(item_data)

        with open('save/save_file.pkl', 'wb') as file:
            pickle.dump(items_data, file)

    def save_file_as(self):
        file_path, _ = QFileDialog.getSaveFileName(self, 'Save File', '', 'Pickle Files (*.pkl)')
        if file_path:
            items_data = []
            for item in self.scene.items():
                if isinstance(item, CustomItem):
                    item_data = {
                        'type': type(item).__name__,
                        'pos': (item.scenePos().x(), item.scenePos().y()),
                        'connect_minus': item.wire_connection_minus,
                        'connect_plus': item.wire_connection_plus
                    }
                    items_data.append(item_data)

            with open(file_path, 'wb') as file:
                pickle.dump(items_data, file)

    def load_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, 'Open File', '', 'Pickle Files (*.pkl)')
        if file_path:
            try:
                with open(file_path, 'rb') as file:
                    items_data = pickle.load(file)

                for item_data in items_data:
                    item_name = QtWidgets.QAction(item_data['type'])
                    self.tool_bar_clicked(item_name)
                    for item in self.scene.items():
                        if isinstance(item, CustomItem) and type(item).__name__ == item_data['type']:
                            if item.pos().x != item_data['pos'][0] and item.pos().y() != item_data['pos'][1]:
                                item.setPos(QPointF(item_data['pos'][0], item_data['pos'][1]))
                                item.wire_connection_plus = item_data['connect_plus']
                                item.wire_connection_minus = item_data['connect_minus']
                self.recovery_connect()
            except Exception as e:
                print(f"An error occurred while loading the file: {e}")

    def recovery_connect(self):
        for item in self.scene.items():
            if isinstance(item, CustomItem) and (item.wire_connection_minus or item.wire_connection_plus):
                if item.wire_connection_minus:
                    minus = item.connect_minus
                    for item2 in self.scene.items():
                        if isinstance(item2, CustomItem) and item.name in item2.wire_connection_plus:
                                plus = item2.connect_plus
                                newConnection = Connection(plus, plus.pos())
                                newConnection.setEnd(minus)
                                self.scene.addItem(newConnection)
                                minus.addLine(newConnection)
                                plus.addLine(newConnection)
                                newConnection.add_connection()

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

    def undo(self):
        if self.scene.items():
            last = self.scene.items()
            if isinstance(last[0], ControlPoint):
                self.for_redo += last[0:3]
                self.scene.removeItem(last[0] and last[1] and last[2])
            elif isinstance(last[0], Connection):
                self.for_redo += last[0:1]
                for item in self.scene.items():
                    if isinstance(item, Connection) and item == last[0]:
                        item.delete_connection()
                        start = item.start
                        end = item.end
                        start.removeLine(item)
                        end.removeLine(item)
                        self.scene.removeItem(last[0])

    def redo(self):
        if self.for_redo:
            if isinstance(self.for_redo[0], ControlPoint):
                rev_redo = self.for_redo[::-1]
                for item in rev_redo:
                    if isinstance(item, CustomItem) and item == rev_redo[0]:
                        self.scene.addItem(item)
                del rev_redo[0:3]
                self.for_redo = rev_redo[::-1]
            elif isinstance(self.for_redo[0], Connection):
                for item in self.for_redo[::-1]:
                    if isinstance(item, Connection) and item == self.for_redo[0]:
                        try:
                            start = item.start
                            end = item.end
                            item.setEnd(end)
                            self.scene.addItem(item)
                            start.addLine(item)
                            end.addLine(item)
                            item.add_connection()
                            del self.for_redo[0]
                        except Exception as e:
                            print(f"An error occurred while redo: {e}")

    def menu_bar_clicked(self, action):
        if action.text() == "Save":
            self.save_file()
        elif action.text() == "Save":
            self.save_file_as()
        elif action.text() == "Open":
            self.load_file()
        elif action.text() == "Undo":
            self.undo()
        elif action.text() == "Redo":
            self.redo()

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
                    self.newConnection.add_connection()
                else:
                    # delete the connection if it exists; remove the following
                    # line if this feature is not required
                    self.newConnection.delete_connection()
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
                                return item2.connect_minus
                elif item.connect_minus == self.start:
                    for item2 in self.scene().items():
                        if isinstance(item2, CustomItem):
                            if item2.connect_plus == self.end:
                                item.wire_connection_minus.append(item2.name)
                                item2.wire_connection_plus.append(item.name)

    def delete_connection(self):
        for item in self.scene().items():
            if isinstance(item, CustomItem):
                if item.connect_plus == self.start:
                    for item2 in self.scene().items():
                        if isinstance(item2, CustomItem):
                            if item2.connect_minus == self.end:
                                item.wire_connection_plus.remove(item2.name)
                                item2.wire_connection_minus.remove(item.name)
                elif item.connect_minus == self.start:
                    for item2 in self.scene().items():
                        if isinstance(item2, CustomItem):
                            if item2.connect_plus == self.end:
                                item.wire_connection_minus.remove(item2.name)
                                item2.wire_connection_plus.remove(item.name)
                else:
                    print('Net')


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
        self.pixmap = pixmap
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
                if any(x in item.wire_connection_plus for x in ["Battery", "Accumulator"]) and \
                        any(x in item.wire_connection_minus for x in ["Battery", "Accumulator", "Key"]):
                    item.setPixmap(QPixmap('Tools/lamp_on.png').scaled(60, 60))
            if isinstance(item, Fan):
                if any(x in item.wire_connection_plus for x in ["Battery", "Accumulator"]) and \
                        any(x in item.wire_connection_minus for x in ["Battery", "Accumulator", "Key"]):
                    item.level(item)
                    item.start()
    elif on:
        for item in scene.items():
            if isinstance(item, Lamp):
                item.setPixmap(QPixmap('Tools/lamp_off.png').scaled(60, 60))
            if isinstance(item, Fan):
                item.stop()
