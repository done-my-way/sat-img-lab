from PyQt5.QtWidgets import (QApplication, QWidget, QLabel, QPushButton,
QHBoxLayout, QGridLayout, QAction, QFileDialog)
from PyQt5.QtGui import QPixmap, QCursor
from PyQt5.QtCore import pyqtSignal, Qt
import sys
import os
from imageio import imread

class Canvas(QLabel):

    hovered = pyqtSignal(int, int)

    def __init__(self, parent):
        super().__init__(parent)
        self.setStyleSheet("background-color: rgb(255,0,0); margin:5px; border:1px solid rgb(0, 255, 0); ")
        self.setMouseTracking(True)

    def mousePressEvent(self, e):
        x_max = self.width()
        y_max = self.height()        
        if (e.x() <= x_max) and (e.y() <= y_max):
            self.hovered.emit(e.x(), e.y())


class myGUI(QWidget):

    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):

        self.tile_cash = []
        
        self.lbl = Canvas(self)
        self.btn_done = QPushButton(self)
        self.btn_type_1 = QPushButton(self)
        self.btn_type_2 = QPushButton(self)
        self.btn_type_1.setText('Lake')
        self.btn_type_2.setText('Forest')
        self.btn_done.setText('DONE')
        pixm = QPixmap('mcq.jpg')
        self.lbl.setPixmap(pixm)
        grid = QGridLayout()
        grid.addWidget(self.lbl, 0, 0, Qt.AlignCenter)
        grid.addWidget(self.btn_type_1, 0, 1, Qt.AlignTop)
        grid.addWidget(self.btn_type_2, 0, 1, Qt.AlignBaseline)
        grid.addWidget(self.btn_done, 0, 1, Qt.AlignBottom)
        self.setLayout(grid)
        self.lbl.hovered.connect(self.p)
        self.btn_type_1.pressed.connect(self.showDialog)
        self.btn_type_2.pressed.connect(lambda: self.mark_as(2))
        self.btn_done.pressed.connect(self.clear_tile_cash)
        self.show()
    
    def showDialog(self):
        self.dir_path = QFileDialog.getExistingDirectoryUrl(self)

        if dir_path:
            self.tiles_list = os.listdir(str(self.dir_path.path()))

    def open_next_tile(self, path):
        path = self.dir_path + '/' + self.tiles_list.pop(0)
        self.img = imread(path)


    def p(self, x, y):
        print(x, y)

    def mark_as(self, n):
        self.tile_cash.append(n)
        print(self.tile_cash)

    def clear_tile_cash(self):
        self.tile_cash = []


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = myGUI()
    sys.exit(app.exec_())