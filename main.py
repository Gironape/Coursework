from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from project_window import Project

import sys


class MainWindow(QWidget):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.main_text = None
        self.btn_start = None
        self.btn_load = None
        self.btn_exit = None
        self.stt = None
        self.setup()
        self.setWindowIcon(QIcon('Tape2.jpg'))
        self.setFont(QFont('Arial', 20))
        self.setStyleSheet("background-color: grey;")

    def setup(self):

        self.setWindowTitle("VCP")
        self.setGeometry(700, 300, 600, 600)

        self.main_text = QLabel(self)
        self.main_text.setText("VCP")
        self.main_text.setFont(QFont('Arial', 30))
        self.main_text.move(260, 50)
        self.main_text.adjustSize()

        self.btn_start = QPushButton(self)
        self.btn_start.setGeometry(150, 200, 300, 30)
        self.btn_start.setText("Старт")
        self.btn_start.clicked.connect(self.start)

        self.btn_load = QPushButton(self)
        self.btn_load.setGeometry(150, 250, 300, 30)
        self.btn_load.setText("Загрузить сохранение")

        self.btn_exit = QPushButton(self)
        self.btn_exit.setGeometry(150, 300, 300, 30)
        self.btn_exit.setText("Выход")
        self.btn_exit.clicked.connect(app.quit)

    def start(self):
        self.stt = Project()
        self.stt.show()
        self.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())
