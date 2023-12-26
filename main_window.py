import pickle
import random
import pyaudio
import wave

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
        self.menuBar = QMenuBar(self)
        self.start_stop = QAction(QIcon('Controls/start.png'), 'Start/Stop', self)
        self.controlbar = QToolBar("My main controlbar")
        self.setWindowIcon(QIcon('VCP.png'))
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
        self.include_id = []

    def closeEvent(self, event) -> None:
        ext = QMessageBox()
        ext.setWindowTitle("Выход")
        ext.setText("Вы действительно хотите выйти?")
        ext.setIcon(QMessageBox.Question)
        ext.setWindowIcon(QIcon('VCP.png'))
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

    def create_menu_bar(self) -> None:
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

    def save_from_file(self) -> str:
        self.file_save_path, _ = QFileDialog.getSaveFileName(self, 'Save File', '', 'Pickle Files (*.pkl)')
        print(type(self.file_save_path))
        return self.file_save_path

    def save_file(self) -> None:
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

    def load_from_file(self) -> str:
        self.file_path, _ = QFileDialog.getOpenFileName(self, 'Open File', '', 'Pickle Files (*.pkl)')
        return self.file_path

    def load_file(self) -> None:
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
                            if not (item.wire_connection_plus and item.wire_connection_minus):
                                item.setPos(QPointF(item_data['pos'][0], item_data['pos'][1]))
                                item.wire_connection_plus = item_data['connect_plus']
                                item.wire_connection_minus = item_data['connect_minus']
                                item.id_connection_plus = item_data['id_plus']
                                item.id_connection_minus = item_data['id_minus']
                                item.id = item_data['id']
                self.recovery_connect()
            except Exception as e:
                print(f"An error occurred while loading the file: {e}")

    def recovery_connect(self) -> None:
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

    def create_tool_bar(self) -> None:
        battery = QAction(QIcon('Tools/battery.png'), 'Battery', self)
        key = QAction(QIcon('Tools/key.png'), 'Key', self)
        lamp = QAction(QIcon('Tools/lamp_off.png'), 'Lamp', self)
        fan = QAction(QIcon('Tools/fan.gif'), 'Fan', self)
        accumulator = QAction(QIcon('Tools/accumulator.png'), 'Accumulator', self)
        speaker = QAction(QIcon('Tools/speaker.png'), 'Speaker', self)
        micro = QAction(QIcon('Tools/micro.png'), 'Microphone', self)

        self.toolbar = self.addToolBar('tools')
        self.toolbar.addAction(battery)
        self.toolbar.addAction(key)
        self.toolbar.addAction(lamp)
        self.toolbar.addAction(accumulator)
        self.toolbar.addAction(fan)
        self.toolbar.addAction(speaker)
        self.toolbar.addAction(micro)
        self.toolbar.setFixedHeight(100)
        self.toolbar.setIconSize(QSize(50, 50))

        self.toolbar.actionTriggered.connect(self.tool_bar_clicked)

    def create_control_bar(self) -> None:
        next_track = QAction(QIcon('Controls/next.png'), 'Next melody', self)
        prev = QAction(QIcon('Controls/prev.png'), 'Previous melody', self)
        rand = QAction(QIcon('Controls/random.png'), 'Random melody', self)
        rec = QAction(QIcon('Controls/recording.png'), 'Record', self)
        listen = QAction(QIcon('Controls/listening.jpg'), 'Listen', self)
        sld = QtWidgets.QSlider(QtCore.Qt.Horizontal, self)
        sld.setFixedSize(100, 20)
        sld.setValue(100)
        separator = QLabel('', self)
        separator.setFixedWidth(50)

        self.controlbar = self.addToolBar('controls')
        self.controlbar.addAction(self.start_stop)
        self.controlbar.addAction(prev)
        self.controlbar.addAction(next_track)
        self.controlbar.addAction(rand)
        self.controlbar.addWidget(sld)
        self.controlbar.addWidget(separator)
        self.controlbar.addAction(rec)
        self.controlbar.addAction(listen)
        self.controlbar.setFixedHeight(100)
        self.controlbar.setIconSize(QSize(50, 50))
        self.controlbar.actionTriggered.connect(self.control_bar_clicked)
        sld.valueChanged.connect(self.slider_changed)

    def undo(self) -> None:
        if self.scene.items():
            last = self.scene.items()
            if isinstance(last[0], ControlPoint):
                self.for_redo += last[0:3]
                self.scene.removeItem(last[0] and last[1] and last[2])
            elif isinstance(last[0], Connection):
                self.for_redo += last[0:1]
                for item in self.scene.items():
                    if isinstance(item, Connection) and item == last[0]:
                        self.check_include(item)
                        item.delete_connection()
                        start = item.start
                        end = item.end
                        start.removeLine(item)
                        end.removeLine(item)
                        self.scene.removeItem(last[0])
            if not self.scene.items():
                self.removeToolBar(self.controlbar)

    def check_include(self, item) -> None:
        for item2 in self.scene.items():
            if isinstance(item2, CustomItem) and item2.id in self.include_id:
                if (item2.connect_plus in [item.start, item.end]) or (item2.connect_minus in
                                                                      [item.start, item.end]):
                    for item3 in self.scene.items():
                        if isinstance(item3, (Battery, Accumulator)):
                            if ((item3.connect_plus in [item.start, item.end]) or (item3.connect_minus in
                                                                                   [item.start, item.end])) and \
                                    (item3.name in item2.wire_connection_plus or item3.name in
                                     item2.wire_connection_minus):
                                include(item2, self.scene, self.include_id, on=True)

    def redo(self) -> None:
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

    def clear_all(self) -> None:
        if self.scene.items():
            self.scene.clear()
            global id_elem
            id_elem = 0
            self.removeToolBar(self.controlbar)

    def menu_bar_clicked(self, action) -> None:
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

    def tool_bar_clicked(self, btn) -> None:
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
        elif btn.text() == "Microphone":
            micro = QPixmap('Tools/micro.png')
            micro_item = Microphone(micro.scaled(60, 60))
            self.scene.addItem(micro_item)

    def control_bar_clicked(self, button) -> None:
        if button.text() == "Start/Stop":
            self.start_stop_button()
        elif button.text() == "Next melody":
            self.checker_action(True)
        elif button.text() == "Previous melody":
            self.checker_action(False)
        elif button.text() == "Random melody":
            self.rand_melody()
        elif button.text() == "Record":
            self.record_voice()
        elif button.text() == "Listen":
            self.listen_voice()

    def record_voice(self) -> None:
        for item in self.scene.items():
            if isinstance(item, Microphone) and item.id in self.include_id:
                item.record_audio()
        self.message_for_user()

    def listen_voice(self) -> None:
        for item in self.scene.items():
            if isinstance(item, Speaker) and item.id in self.include_id:
                item.listen_record()
                return
        self.message_for_user()

    def checker_action(self, switch):
        for item in self.scene.items():
            if isinstance(item, Speaker) and switch and item.id in self.include_id:
                item.next_melody()
                return
            elif isinstance(item, Speaker) and not switch and item.id in self.include_id:
                item.prev_melody()
                return
        self.message_for_user()

    def rand_melody(self) -> None:
        for item in self.scene.items():
            if isinstance(item, Speaker) and item.id in self.include_id:
                item.random_melody()
                return
        self.message_for_user()

    def slider_changed(self, value) -> None:
        for item in self.scene.items():
            if isinstance(item, Speaker) and item.id in self.include_id:
                item.set_volume(value)
                return
        self.message_for_user()

    def start_stop_button(self) -> None:
        if self.start_stop.property("state") is None or self.start_stop.property("state") == "on":
            self.start_stop.setIcon(QIcon('Controls/stop.png'))
            self.start_stop.setProperty("state", "off")
            for item in self.scene.items():
                if isinstance(item, (Lamp, Speaker, Fan, Microphone)) and not self.include_id.count(item.id):
                    include(item, self.scene, self.include_id, on=False)
        else:
            self.start_stop.setIcon(QIcon('Controls/start.png'))
            self.start_stop.setProperty("state", "on")
            for item in self.scene.items():
                if isinstance(item, (Lamp, Speaker, Fan, Microphone)):
                    include(item, self.scene, self.include_id, on=True)

    def message_for_user(self) -> None:
        err = QMessageBox()
        err.setWindowTitle("Информация")
        err.setText("Данное действие пока не доступно")
        err.setIcon(QMessageBox.Information)
        err.setWindowIcon(QIcon('VCP.png'))
        err.setStandardButtons(QMessageBox.Close)
        err.setInformativeText("Дополнительная информация")
        err.setDetailedText('Данные инструменты предназначены для управления элементами схемы. Чтобы их использовать,'
                            ' подключите ваше устройство в сеть и нажмите кнопку "Start"')
        err.exec_()
        if QMessageBox.Close:
            err.close()


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

    def add_connection(self) -> QGraphicsItem:
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

    def delete_connection(self) -> None:
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

    def addLine(self, lineItem) -> bool:
        for existing in self.lines:
            if existing.controlPoints() == lineItem.controlPoints():
                # another line with the same control points already exists
                return False
        self.lines.append(lineItem)
        return True

    def removeLine(self, lineItem) -> bool:
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
        self.timer.start(100)

    def stop(self):
        self.timer.stop()


class Speaker(CustomItem):
    def __init__(self, pixmap, minus=True, plus=True, parent=None):
        super().__init__(pixmap, minus, plus, parent)
        self.name = "Speaker"
        self.player = QMediaPlayer()
        self.playlist = QMediaPlaylist()
        self.play_list()
        self.player.setPlaylist(self.playlist)
        self.position = self.player.position()

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
        self.playlist.setCurrentIndex(random_index)
        self.position = 0
        self.player.play()

    def play_list(self):
        self.playlist.addMedia(QMediaContent(QUrl.fromLocalFile('Speaker/1.mp3')))
        self.playlist.addMedia(QMediaContent(QUrl.fromLocalFile('Speaker/2.mp3')))
        self.playlist.addMedia(QMediaContent(QUrl.fromLocalFile('Speaker/3.mp3')))
        self.playlist.addMedia(QMediaContent(QUrl.fromLocalFile('Speaker/4.mp3')))
        self.playlist.addMedia(QMediaContent(QUrl.fromLocalFile('Speaker/5.mp3')))
        self.playlist.addMedia(QMediaContent(QUrl.fromLocalFile('save/output.wav')))
        self.playlist.setCurrentIndex(0)

    def set_volume(self, value):
        self.player.setVolume(value)

    def listen_record(self):
        self.playlist.setCurrentIndex(self.playlist.mediaCount() - 1)
        self.position = 0
        self.player.play()


class Microphone(CustomItem):
    def __init__(self, pixmap, minus=True, plus=True, parent=None):
        super().__init__(pixmap, minus, plus, parent)

        self.name = "Microphone"

    def record_audio(self):
        # Задаем параметры записи
        FORMAT = pyaudio.paInt16
        CHANNELS = 1
        RATE = 44100
        CHUNK = 1024
        RECORD_SECONDS = 5
        WAVE_OUTPUT_FILENAME = "save/output.wav"

        # Создаем объект PyAudio
        audio = pyaudio.PyAudio()

        # Открываем поток для записи
        stream = audio.open(format=FORMAT, channels=CHANNELS,
                            rate=RATE, input=True,
                            frames_per_buffer=CHUNK)

        print("Recording...")

        # Записываем звуковой сигнал в буфер
        frames = []
        for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
            data = stream.read(CHUNK)
            frames.append(data)

        print("Finished recording.")

        # Останавливаем поток и закрываем объект PyAudio
        stream.stop_stream()
        stream.close()
        audio.terminate()

        # Сохраняем записанный звуковой сигнал в файл
        wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(audio.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))
        wf.close()


def include(item, scene, include_id, on):
    electrical_elements = []
    if not on:
        try:
            serial_elements(item, scene, electrical_elements)
            print(electrical_elements)
            if any(x in electrical_elements for x in item.id_connection_plus) and \
                    any(x in electrical_elements for x in item.id_connection_minus):
                include_id.append(item.id)
                if len(item.id_connection_plus) >= 2 and len(item.id_connection_minus) >= 2:
                    parallel_connection(item, scene, include_id)
            elif any(x in electrical_elements for x in item.id_connection_plus):
                include_id.append(item.id)
                serial_connection(item, scene, include_id, electrical_elements)
            for item3 in scene.items():
                if isinstance(item3, Lamp) and item3.id in include_id:
                    item3.setPixmap(QPixmap('Tools/lamp_on.png').scaled(60, 60))
                elif isinstance(item3, Fan) and item3.id in include_id:
                    item3.start()
                elif isinstance(item3, Speaker) and item3.id in include_id:
                    item3.play_audio()
        except Exception as e:
            print(f"An error occurred while include: {e}")
    elif on:
        if isinstance(item, Lamp) and item.id in include_id:
            item.setPixmap(QPixmap('Tools/lamp_off.png').scaled(60, 60))
            include_id.remove(item.id)
        elif isinstance(item, Fan) and item.id in include_id:
            item.stop()
            include_id.remove(item.id)
        elif isinstance(item, Speaker) and item.id in include_id:
            item.stop_audio()
            include_id.remove(item.id)
        elif isinstance(item, Microphone) and item.id in include_id:
            include_id.remove(item.id)
        print('uydfs', include_id)
        return include_id


def parallel_connection(item, scene, include_id):
    for item2 in scene.items():
        if isinstance(item2, (Lamp, Fan, Speaker, Microphone, Key)) and not include_id.count(
                item2.id) and item2.id != item.id:
            if item2.id_connection_plus.count(item.id) and item2.id_connection_minus.count(item.id):
                include_id.append(item2.id)
                if len(item2.id_connection_plus) == len(item2.id_connection_minus) >= 2:
                    return parallel_connection(item2, scene, include_id)
                else:
                    return parallel_connection(item, scene, include_id)
    return include_id


def serial_connection(item, scene, include_id, el_elem):
    for item2 in scene.items():
        if isinstance(item2, CustomItem) and not el_elem.count(item2.id) and not include_id.count(item2.id):
            if item.id_connection_minus.count(item2.id) and not any(x in el_elem for x in item2.id_connection_minus):
                include_id.append(item2.id)
                return serial_connection(item2, scene, include_id, el_elem)
            elif item.id_connection_minus.count(item2.id) and any(x in el_elem for x in item2.id_connection_minus):
                include_id.append(item2.id)
                return include_id


def serial_elements(item, scene, electrical_elements):
    for elem in scene.items():
        if isinstance(elem, (Battery, Accumulator, Key)) and not electrical_elements.count(elem):
            if item.id in elem.id_connection_plus and item.id in elem.id_connection_minus:
                electrical_elements.append(elem.id)
                return electrical_elements
            elif not any(x in elem.wire_connection_plus for x in ['Battery', 'Accumulator', 'Key']) and not\
                    any(x in elem.wire_connection_minus for x in ['Battery', 'Accumulator', 'Key']):
                electrical_elements.append(elem.id)
                return electrical_elements
                pass
            elif item.id not in elem.id_connection_plus and item.id in elem.id_connection_minus:
                if any(x in elem.wire_connection_plus for x in ['Battery', 'Accumulator', 'Key']):
                    electrical_elements.append(elem.id)
                    return serial_elements(elem, scene, electrical_elements)
                else:
                    electrical_elements.append(elem.id)
                    return electrical_elements
            elif item.id not in elem.id_connection_minus:
                if any(x in elem.id_connection_minus for x in electrical_elements) and \
                        any(x in elem.wire_connection_plus for x in ['Lamp', 'Fan', 'Speaker', 'Microphone', 'Key']):
                    electrical_elements.append(elem.id)
                    return electrical_elements
