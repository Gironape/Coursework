from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from main_window import Project

import sys


class StartWindow(QWidget):
    def __init__(self):
        super(StartWindow, self).__init__()
        self.main_text = QLabel(self)
        self.btn_start = QPushButton(self)
        self.btn_load = QPushButton(self)
        self.btn_exit = QPushButton(self)
        self.project = Project()
        self.setup()
        self.setWindowIcon(QIcon('VCP.png'))
        self.setFont(QFont('Arial', 20))

        self.setStyleSheet("background-color: rgb(150, 150, 150);")

    def setup(self) -> None:

        self.setWindowTitle("VCP")
        self.setGeometry(700, 300, 600, 600)

        self.main_text.setText("VCP")
        self.main_text.setFont(QFont('Arial', 30))
        self.main_text.move(260, 50)
        self.main_text.adjustSize()

        self.btn_start.setGeometry(150, 200, 300, 30)
        self.btn_start.setText("Старт")
        self.btn_start.clicked.connect(self.start)

        self.btn_load.setGeometry(150, 250, 300, 30)
        self.btn_load.setText("Загрузить сохранение")
        self.btn_load.clicked.connect(self.load)

        self.btn_exit.setGeometry(150, 300, 300, 30)
        self.btn_exit.setText("Выход")
        self.btn_exit.clicked.connect(app.quit)

    def start(self) -> None:
        self.project = Project()
        self.project.show()
        self.close()

    def load(self) -> None:
        self.project = Project()
        if self.project.load_from_file():
            self.project.show()
            self.project.load_file()
            self.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = StartWindow()
    win.show()
    sys.exit(app.exec_())
