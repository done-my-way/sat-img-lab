from PyQt5.QtWidgets import (QApplication, QWidget, QLabel, QPushButton,
QHBoxLayout, QGridLayout, QAction, QFileDialog, QSlider, QSizeGrip)
from PyQt5.QtGui import QPixmap, QCursor, QImage
from PyQt5.QtCore import pyqtSignal, Qt
import sys
import os
from imageio import imread, imwrite
import tempfile
from numpy import uint8, ones
from collections import namedtuple

from pathlib import Path

import cv2
import numpy 
import matplotlib.pyplot as plt

# needed to pass selected point coordinates to the cv2.floodFill()
Point = namedtuple('Point', 'x, y')

class Canvas(QLabel):

    """ Allows relative position tracking  within an image."""

    pressed = pyqtSignal(int, int)

    def __init__(self, parent):
        super().__init__(parent)
        self.setWindowFlag(Qt.SubWindow)
        self.setMouseTracking(True)
        self.grip1 = QSizeGrip(self)
        self.layout = QHBoxLayout(self)
        self.layout.addWidget(self.grip1, 0, Qt.AlignRight | Qt.AlignBottom)

    def mousePressEvent(self, e):
        x_max = self.width()
        y_max = self.height()
        # if the cursor is within the image (label)        
        if (e.x() <= x_max) and (e.y() <= y_max):
            self.pressed.emit(e.x(), e.y())

    # def resizeEvent (self, e):
    #     x = self.width()
    #     y = self.height()
    #     pixmap4 = self.pixmap().scaled(x, y, Qt.KeepAspectRatio)
    #     self.setPixmap(pixmap4)
    #     self.show()

class myGUI(QWidget):

    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):

        self._x2_pressed = False

        self._x_scale = 1
        self._y_scale = 1

        self._x = 0
        self._y = 0

        self.tile_cash = []
        
        self.lbl = Canvas(self)

        self.btn_next = QPushButton(self)
        self.btn_open = QPushButton(self)
        self.btn_type_1 = QPushButton(self)

        self.btn_open.setText('Open')
        self.btn_type_1.setText('x2')
        self.btn_next.setText('Next')

        pixm = QPixmap('plug.jpg')
        self.img = imread('plug.jpg')
        self.img = self.img.astype(uint8)
        self.lbl.setPixmap(pixm)
        self.btn_next.setVisible(False)

        self._ih = pixm.height()
        self._iw = pixm.width()

        self.sld = QSlider(Qt.Horizontal, self)
        self.sld.setFixedSize(500, 30)
        self.sld.setMaximum(255)
        self.sld.setMinimum(0)
        self.sld.setValue(20)
        self.sld.setTickPosition(QSlider.TicksBelow)
        self.sld.setTickInterval(10)
        

        grid = QGridLayout()
        grid.addWidget(self.lbl, 0, 0, Qt.AlignCenter)
        grid.addWidget(self.btn_open, 0, 1, Qt.AlignTop)
        grid.addWidget(self.btn_type_1, 0, 1, Qt.AlignBaseline)
        grid.addWidget(self.btn_next, 0, 1, Qt.AlignBottom)
        grid.addWidget(self.sld, 1, 0, Qt.AlignCenter)
        self.setLayout(grid)

        self.lbl.pressed.connect(self.magic_wand)
        # btn_open opens a dialogue for selecting a directory
        # containing the images to label.
        self.btn_open.pressed.connect(self.showDialog)
        self.btn_type_1.pressed.connect(lambda: self.mark_as(1))
        # btn_next opens the next image from the directory.
        self.btn_next.pressed.connect(self.clear_tile_cash)
        self.btn_next.pressed.connect(self.open_file)
        # sld controls the FloodFill threshold value
        self.sld.valueChanged.connect(self.change_thresh)
        #
        self.btn_type_1.pressed.connect(self.x2)
        self.show()
    
    def showDialog(self):

        """ Open directory selection dialogue"""

        self.dir_path = QFileDialog.getExistingDirectoryUrl(self).path()

        if self.dir_path:
            self.tiles_list = os.listdir(str(self.dir_path))
            self.btn_next.setVisible(True)

    def open_file(self):

        """ Open the next tif file from the chosen directory.
            The .tif file is opened - saved as jpg (by ) - and reopened as jpg.
        """
        self._x_scale = 1
        self._y_scale = 1
        self._x2_pressed = False
        
        path = Path(self.dir_path, self.tiles_list.pop())      
        self.img = imread(path)
        self._qimg = QImage(self.img.data, self.img.shape[1], self.img.shape[0], self.img.strides[0], QImage.Format_RGB888)
        print(self.img.__dict__)

        pixm = QPixmap(self._qimg)
        self.lbl.setPixmap(pixm)

        self._ih = pixm.height()
        self._iw = pixm.width()

    def change_thresh(self, thresh):
        self.magic_wand(self._x * self._x_scale, self._y * self._y_scale, thresh)


    def print_coordinates(self, x, y):
        print(x, y)

    def magic_wand(self, x, y, thresh=25):

        """Choose a connected component and show the chosen region"""

        # move slider to the initial position
        self.sld.setValue(thresh)
        # change seedPoint coordinates
        print(x, y)
        self._x = x // self._x_scale
        self._y = y // self._y_scale      
        seedPoint = Point(self._x, self._y)
        # number of neighbour pixels considered | value to fill the mask
        flags = 4 | (1 << 8)
        # compare considered points to the seed | do not change the pic itself
        flags |= cv2.FLOODFILL_FIXED_RANGE |  cv2.FLOODFILL_MASK_ONLY
        self._mask = numpy.zeros((self._ih+2, self._iw+2), dtype=uint8)
        # changes the mask inplace
        cv2.floodFill(self.img, self._mask, seedPoint, 0, (thresh,)*3, (thresh,)*3, flags)

        self._selection = numpy.zeros((self._ih, self._iw, 3), dtype=uint8)
        self._selection[:, :, 0] = numpy.multiply(self.img[:, :, 0], self._mask[1:-1, 1:-1])
        self._selection[:, :, 1] = numpy.multiply(self.img[:, :, 1], self._mask[1:-1, 1:-1])
        self._selection[:, :, 2] = numpy.multiply(self.img[:, :, 2], self._mask[1:-1, 1:-1])

        # contours to represent the selection
        contours, hierarchy = cv2.findContours(self._mask[1:-1, 1:-1], cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        contour = cv2.drawContours(self.img.copy(), contours, -1, (128, 128, 0), 1)

        applied_mask = QImage(contour.data, contour.shape[1], contour.shape[0], contour.strides[0], QImage.Format_RGB888)
        pixm = QPixmap(applied_mask)

        self.lbl.setPixmap(pixm.scaled(self.lbl.pixmap().width(),self.lbl.pixmap().height(), Qt.KeepAspectRatio))

    def x2(self):

        # toggle between x2-enlarged and real-size image

        pixm = self.lbl.pixmap()
        y = self.lbl.pixmap().height()
        x = self.lbl.pixmap().width()

        if self._x2_pressed == True:
            self.lbl.setPixmap(pixm.scaled(x // 2, y // 2, Qt.KeepAspectRatio))
            self._x_scale = self._x_scale // 2
            self._y_scale = self._y_scale // 2
            self._x2_pressed = False
        else:
            self.lbl.setPixmap(pixm.scaled(x * 2, y * 2, Qt.KeepAspectRatio))
            self._x_scale = self._x_scale * 2
            self._y_scale = self._y_scale * 2
            self._x2_pressed = True


    def mark_as(self, n):

        """ Add number corresponding to the surface type to an
        array associated with the opened image."""

        self.tile_cash.append(n)
        #print(self.tile_cash)

    def clear_tile_cash(self):

        """ Clear the surface obsects array associated with the 
        opened image. """

        self.tile_cash = []


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = myGUI()
    sys.exit(app.exec_())