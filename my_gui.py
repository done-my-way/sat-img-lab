from PyQt5.QtWidgets import (QApplication, QWidget, QLabel, QPushButton,
QHBoxLayout, QGridLayout, QAction, QFileDialog)
from PyQt5.QtGui import QPixmap, QCursor
from PyQt5.QtCore import pyqtSignal, Qt
import sys
import os
from imageio import imread, imwrite
import tempfile
from numpy import uint8

class Canvas(QLabel):

    """ Allows position tracking relative within an image."""

    pressed = pyqtSignal(int, int)

    def __init__(self, parent):
        super().__init__(parent)
        self.setStyleSheet("background-color: rgb(255,0,0); margin:0px; border:1px solid rgb(0, 255, 0)") # ; max-height:600px; min-height:600px; max-width:600px; min-width:600px")
        self.setMouseTracking(True)

    def mousePressEvent(self, e):
        x_max = self.width()
        y_max = self.height()
        # if the cursor is within the image (label)        
        if (e.x() <= x_max) and (e.y() <= y_max):
            self.pressed.emit(e.x(), e.y())


class myGUI(QWidget):

    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):

        self.tile_cash = []
        
        self.lbl = Canvas(self)

        self.btn_next = QPushButton(self)
        self.btn_open = QPushButton(self)
        self.btn_type_1 = QPushButton(self)

        self.btn_open.setText('Open')
        self.btn_type_1.setText('Type: Forest')
        self.btn_next.setText('Next')

        pixm = QPixmap('test.jpg').scaled(600, 600, Qt.KeepAspectRatio)
        self.lbl.setPixmap(pixm)
        self.btn_next.setVisible(False)

        grid = QGridLayout()
        grid.addWidget(self.lbl, 0, 0, Qt.AlignCenter)
        grid.addWidget(self.btn_open, 0, 1, Qt.AlignTop)
        grid.addWidget(self.btn_type_1, 0, 1, Qt.AlignBaseline)
        grid.addWidget(self.btn_next, 0, 1, Qt.AlignBottom)
        self.setLayout(grid)

        self.lbl.pressed.connect(self.print_coordinates)
        # btn_open opens a dialogue for selecting a directory
        # containing the images to label.
        self.btn_open.pressed.connect(self.showDialog)
        self.btn_type_1.pressed.connect(lambda: self.mark_as(1))
        # btn_next opens the next image from the directory.
        self.btn_next.pressed.connect(self.clear_tile_cash)
        self.btn_next.pressed.connect(self.open_tif_file)

        self.show()
    
    def showDialog(self):

        """ Open directory selection dialogue"""

        self.dir_path = QFileDialog.getExistingDirectoryUrl(self).path()

        if self.dir_path:
            self.tiles_list = os.listdir(str(self.dir_path))
            self.btn_next.setVisible(True)

    def open_tif_file(self):

        """ Open the next tif file from the chosen directory.
            The .tif file is opened - saved as jpg (by ) - and reopened as jpg.
        """

        path = self.dir_path + '/' + self.tiles_list.pop()        
        img = imread(path)
        img = img.astype(uint8)
        imwrite('temp.jpg', img, format='jpg')
        pixm = QPixmap('temp.jpg').scaled(600, 600, Qt.KeepAspectRatio)
        self.lbl.setPixmap(pixm)

        os.remove('temp.jpg')


    def print_coordinates(self, x, y):
        print(x, y)

    def mark_as(self, n):

        """ Add number corresponding to the surface type to an
        array associated with the opened image."""

        self.tile_cash.append(n)
        print(self.tile_cash)

    def clear_tile_cash(self):

        """ Clear the surface obsects array associated with the 
        opened image. """

        self.tile_cash = []


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = myGUI()
    sys.exit(app.exec_())