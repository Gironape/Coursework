from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMainWindow, QApplication

import sys


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.main_text = None
        self.btn_new = None
        self.btn_load = None
        self.btn_exit = None
        self.setup()

    def setup(self):

        self.setWindowTitle("Virtual constructor")
        self.setGeometry(700, 540, 600, 600)

        self.main_text = QtWidgets.QLabel(self)
        self.main_text.setText("Hello")
        self.main_text.move(290, 50)
        self.main_text.adjustSize()

        self.btn_new = QtWidgets.QPushButton(self)
        self.btn_new.move(200, 200)
        self.btn_new.setText("Старт")
        self.btn_new.setFixedWidth(200)

        self.btn_load = QtWidgets.QPushButton(self)
        self.btn_load.move(200, 250)
        self.btn_load.setText("Загрузить сохранение")
        self.btn_load.setFixedWidth(200)

        self.btn_exit = QtWidgets.QPushButton(self)
        self.btn_exit.move(200, 300)
        self.btn_exit.setText("Выход")
        self.btn_exit.setFixedWidth(200)
        self.btn_exit.clicked.connect(app.quit)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())


