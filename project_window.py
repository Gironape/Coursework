import pickle
import random

from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent, QMediaPlaylist
from PyQt5.QtWidgets import *

id_elem = 0


class Project(QMainWindow):
    def __init__(self):
        super(Project, self).__init__()
        self.file_save_path = None
        self.toolbar = QToolBar("My main toolbar")
        self.menuBar = None
        self.start_stop = None
        self.controlbar = QToolBar("My main controlbar")
        self.setWindowIcon(QIcon('Tape2.jpg'))
        self.setFont(QFont('Arial', 20))
        self.setStyleSheet("background-color:;")
        self.setWindowTitle("VCP")
        self.setGeometry(0, 0, 1920, 1080)
        self.create_menu_bar()
        self.create_tool_bar()
        self.scene = Scene()
        self.view = QGraphicsView(self.scene)
        self.setCentralWidget(self.view)
        self.for_redo = []

    def closeEvent(self, event):
        ext = QMessageBox()
        ext.setWindowTitle("Выход")
        ext.setText("Вы действительно хотите выйти?")
        ext.setIcon(QMessageBox.Question)
        ext.setWindowIcon(QIcon('Tape2.jpg'))
        ext.setStandardButtons(QMessageBox.Save | QMessageBox.Yes | QMessageBox.Close)
        ext.setInformativeText("Сохраните проект перед выходом")
        result = ext.exec_()
        if result == QMessageBox.Save:
            self.save_file()
            event.accept()
        elif result == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()

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
        clear = QAction('Clear all', self)
        clear.setIcon(QIcon('Menu/clear.png'))
        editMenu.addAction(undo)
        editMenu.addAction(redo)
        editMenu.addAction(clear)
        editMenu.triggered[QAction].connect(self.menu_bar_clicked)

        # РАЗОБРАТЬСЯ С СОХРАНЕНИЕМ

    def save_from_file(self):
        self.file_save_path, _ = QFileDialog.getSaveFileName(self, 'Save File', '', 'Pickle Files (*.pkl)')
        return self.file_save_path

    def save_file(self):
        if self.file_save_path:
            file_path = self.file_save_path
        else:
            file_path = 'save/save_file.pkl'

        if file_path:
            items_data = []
            for item in self.scene.items():
                if isinstance(item, CustomItem):
                    item_data = {
                        'type': type(item).__name__,
                        'pos': (item.scenePos().x(), item.scenePos().y()),
                        'connect_minus': item.wire_connection_minus,
                        'connect_plus': item.wire_connection_plus,
                        'id_plus': item.id_connection_plus,
                        'id_minus': item.id_connection_minus,
                        'id': item.id
                    }
                    items_data.append(item_data)

            with open(file_path, 'wb') as file:
                pickle.dump(items_data, file)
        self.file_save_path = None

    def load_from_file(self):
        self.file_path, _ = QFileDialog.getOpenFileName(self, 'Open File', '', 'Pickle Files (*.pkl)')
        return self.file_path

    def load_file(self):
        global id_elem
        id_elem = 0
        file_path = self.file_path
        if file_path:
            try:
                with open(file_path, 'rb') as file:
                    items_data = pickle.load(file)

                for item_data in items_data:
                    item_name = QtWidgets.QAction(item_data['type'])
                    self.tool_bar_clicked(item_name)
                    for item in self.scene.items():
                        if isinstance(item, CustomItem) and type(item).__name__ == item_data['type']:
                            if not item.wire_connection_plus and not item.wire_connection_minus:
                                item.setPos(QPointF(item_data['pos'][0], item_data['pos'][1]))
                                item.wire_connection_plus = item_data['connect_plus']
                                item.wire_connection_minus = item_data['connect_minus']
                                item.id_connection_plus = item_data['id_plus']
                                item.id_connection_minus = item_data['id_minus']
                                item.id = item_data['id']
                self.recovery_connect()
            except Exception as e:
                print(f"An error occurred while loading the file: {e}")

    def recovery_connect(self):
        for item in self.scene.items():
            if isinstance(item, CustomItem) and item.wire_connection_minus:
                if item.wire_connection_minus:
                    minus = item.connect_minus
                    for item2 in self.scene.items():
                        if isinstance(item2, CustomItem) and item.id in item2.id_connection_plus:
                            plus = item2.connect_plus
                            newConnection = Connection(plus, plus.pos())
                            newConnection.setEnd(minus)
                            self.scene.addItem(newConnection)
                            minus.addLine(newConnection)
                            plus.addLine(newConnection)

    def create_tool_bar(self):
        battery = QAction(QIcon('Tools/battery.png'), 'Battery', self)
        key = QAction(QIcon('Tools/key.png'), 'Key', self)
        lamp = QAction(QIcon('Tools/lamp_off.png'), 'Lamp', self)
        fan = QAction(QIcon('Tools/fan.gif'), 'Fan', self)
        accumulator = QAction(QIcon('Tools/accumulator.png'), 'Accumulator', self)
        speaker = QAction(QIcon('Tools/speaker.png'), 'Speaker', self)

        self.toolbar = self.addToolBar('tools')
        self.toolbar.addAction(battery)
        self.toolbar.addAction(key)
        self.toolbar.addAction(lamp)
        self.toolbar.addAction(accumulator)
        self.toolbar.addAction(fan)
        self.toolbar.addAction(speaker)
        separator = QLabel('', self)
        separator.setFixedWidth(700)  # Устанавливаем фиксированную ширину разделителя
        self.toolbar.addWidget(separator)
        self.toolbar.setFixedHeight(100)
        self.toolbar.setIconSize(QSize(50, 50))

        self.toolbar.actionTriggered.connect(self.tool_bar_clicked)

    def create_control_bar(self):
        self.start_stop = QAction(QIcon('Controls/start.png'), 'Start/Stop', self)
        next_track = QAction(QIcon('Controls/next.png'), 'Next melody', self)
        prev = QAction(QIcon('Controls/prev.png'), 'Previous melody', self)
        rand = QAction(QIcon('Controls/random.png'), 'Random melody', self)
        self.controlbar = self.addToolBar('controls')
        self.controlbar.addAction(self.start_stop)
        self.controlbar.addAction(prev)
        self.controlbar.addAction(next_track)
        self.controlbar.addAction(rand)
        self.controlbar.setFixedHeight(100)
        self.controlbar.setIconSize(QSize(50, 50))
        self.controlbar.actionTriggered.connect(self.control_bar_clicked)

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
            if not self.scene.items():
                self.removeToolBar(self.controlbar)

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

    def clear_all(self):
        if self.scene.items():
            self.scene.clear()
            global id_elem
            id_elem = 0
            self.removeToolBar(self.controlbar)

    def menu_bar_clicked(self, action):
        if action.text() == "Save":
            self.save_file()
        elif action.text() == "Save as":
            self.save_from_file()
            self.save_file()
        elif action.text() == "Open":
            self.load_from_file()
            self.load_file()
        elif action.text() == "Undo":
            self.undo()
        elif action.text() == "Redo":
            self.redo()
        elif action.text() == 'Clear all':
            self.clear_all()

    def tool_bar_clicked(self, btn):
        global id_elem
        id_elem += 1
        if not self.scene.items():
            self.addToolBarBreak()
            self.create_control_bar()
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
        elif btn.text() == "Fan":
            fan = QPixmap('Tools/fan.gif')
            self.fan_item = Fan(fan.scaled(60, 60), gif_path='Tools/fan.gif')
            self.scene.addItem(self.fan_item)
        elif btn.text() == "Accumulator":
            accumulator = QPixmap('Tools/accumulator.png')
            accumulator_item = Accumulator(accumulator.scaled(70, 60))
            self.scene.addItem(accumulator_item)
        elif btn.text() == "Speaker":
            speaker = QPixmap('Tools/speaker.png')
            speaker_item = Speaker(speaker.scaled(60, 60))
            self.scene.addItem(speaker_item)

    def control_bar_clicked(self, button):
        if button.text() == "Start/Stop":
            self.start_stop_button()
        if button.text() == "Next melody":
            self.checker_action(True)
        if button.text() == "Previous melody":
            self.checker_action(False)
        if button.text() == "Random melody":
            self.rand_melody()

    def checker_action(self, switch):
        for item in self.scene. items():
            if isinstance(item, Speaker) and switch:
                item.next_melody()
            elif isinstance(item, Speaker) and not switch:
                item.prev_melody()

    def rand_melody(self):
        for item in self.scene. items():
            if isinstance(item, Speaker):
                item.random_melody()

    def start_stop_button(self):
        if self.start_stop.property("state") is None or self.start_stop.property("state") == "on":
            self.start_stop.setIcon(QIcon('Controls/stop.png'))
            self.start_stop.setProperty("state", "off")
            for item in self.scene.items():
                if isinstance(item, CustomItem):
                    include(item, on=False)
        else:
            self.start_stop.setIcon(QIcon('Controls/start.png'))
            self.start_stop.setProperty("state", "on")
            for item in self.scene.items():
                if isinstance(item, CustomItem):
                    include(item, on=True)


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
                                item.id_connection_plus.append(item2.id)
                                item2.id_connection_minus.append(item.id)
                                return item2.connect_minus
                elif item.connect_minus == self.start:
                    for item2 in self.scene().items():
                        if isinstance(item2, CustomItem):
                            if item2.connect_plus == self.end:
                                item.wire_connection_minus.append(item2.name)
                                item2.wire_connection_plus.append(item.name)
                                item.id_connection_minus.append(item2.id)
                                item2.id_connection_plus.append(item.id)

    def delete_connection(self):
        for item in self.scene().items():
            if isinstance(item, CustomItem):
                if item.connect_plus == self.start:
                    for item2 in self.scene().items():
                        if isinstance(item2, CustomItem):
                            if item2.connect_minus == self.end:
                                item.wire_connection_plus.remove(item2.name)
                                item2.wire_connection_minus.remove(item.name)
                                item.id_connection_plus.remove(item2.id)
                                item2.id_connection_minus.remove(item.id)
                elif item.connect_minus == self.start:
                    for item2 in self.scene().items():
                        if isinstance(item2, CustomItem):
                            if item2.connect_plus == self.end:
                                item.wire_connection_minus.remove(item2.name)
                                item2.wire_connection_plus.remove(item.name)
                                item.id_connection_minus.remove(item2.id)
                                item2.id_connection_plus.remove(item.id)
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
        self.id = id_elem
        self.wire_connection_plus = []
        self.wire_connection_minus = []
        self.id_connection_plus = []
        self.id_connection_minus = []
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
        print(self.name, self.id)


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
            self.lvl = 1
        else:
            self.lvl = 3


class Speaker(CustomItem):
    def __init__(self, pixmap, minus=True, plus=True, parent=None):
        super().__init__(pixmap, minus, plus, parent)
        try:
            self.name = "Speaker"
            self.player = QMediaPlayer()
            self.playlist = QMediaPlaylist()
            self.play_list()
            self.player.setPlaylist(self.playlist)  # Устанавливаем плейлист для плеера
            self.position = self.player.position()  # Инициализируем позицию воспроизведения

        except Exception as e:
            print(f"An error occurred while initializing Speaker: {e}")

    def play_audio(self):
        self.player.setPosition(self.position)
        self.player.play()

    def stop_audio(self):
        self.position = self.player.position()
        self.player.stop()

    def next_melody(self):
        self.playlist.next()
        self.position = 0
        self.player.play()

    def prev_melody(self):
        self.playlist.previous()
        self.position = 0
        self.player.play()

    def random_melody(self):
        random_index = random.randint(0, self.playlist.mediaCount() - 1)
        self.player.setMedia(self.playlist.media(random_index))
        self.position = 0
        self.player.play()

    def play_list(self):
        self.playlist.addMedia(QMediaContent(QUrl.fromLocalFile('Speaker/1.mp3')))
        self.playlist.addMedia(QMediaContent(QUrl.fromLocalFile('Speaker/2.mp3')))
        self.playlist.addMedia(QMediaContent(QUrl.fromLocalFile('Speaker/3.mp3')))
        self.playlist.addMedia(QMediaContent(QUrl.fromLocalFile('Speaker/4.mp3')))
        self.playlist.addMedia(QMediaContent(QUrl.fromLocalFile('Speaker/5.mp3')))
        self.playlist.setCurrentIndex(0)

    def set_volume_down(self):
        self.player.volume() - 10

    def set_volume_up(self):
        self.player.volume() + 10


def include(item, on):
    if not on:
        if any(x in item.wire_connection_plus for x in ["Battery", "Accumulator"]) and \
                any(x in item.wire_connection_minus for x in ["Battery", "Accumulator", "Key"]):
            if isinstance(item, Lamp):
                item.setPixmap(QPixmap('Tools/lamp_on.png').scaled(60, 60))
            elif isinstance(item, Fan):
                item.start()
            elif isinstance(item, Speaker):
                item.play_audio()
    elif on:
        if isinstance(item, Lamp):
            item.setPixmap(QPixmap('Tools/lamp_off.png').scaled(60, 60))
        elif isinstance(item, Fan):
            item.stop()
        elif isinstance(item, Speaker):
            item.stop_audio()
