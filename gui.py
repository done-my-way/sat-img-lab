from PyQt5.QtWidgets import (QApplication, QWidget, QLabel, QPushButton,
QHBoxLayout, QGridLayout, QAction, QFileDialog, QSlider, QSizeGrip, QFrame)
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

# surface types: river, lake (body of water), road, building, firebreak, cloud, cloud shade

class Canvas(QLabel):

    """ Allows relative position tracking  within an image."""

    pressed = pyqtSignal(int, int)

    def __init__(self, parent):
        super().__init__(parent)
        self.setWindowFlag(Qt.SubWindow)
        self.setMouseTracking(True)
        # self.grip1 = QSizeGrip(self)
        # self.layout = QHBoxLayout(self)
        # self.layout.addWidget(self.grip1, 0, Qt.AlignRight | Qt.AlignBottom)

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

        self._toggled = False

        self._x2_pressed = False

        self._x_scale = 1
        self._y_scale = 1

        self._x = 0
        self._y = 0

        self.tile_cash = []
        
        self.lbl = Canvas(self)

        self.btn_next = QPushButton(self)
        self.btn_open = QPushButton(self)
        self.btn_scale = QPushButton(self)

        self.btn_new_mask = QPushButton(self)
        self.btn_save_mask = QPushButton(self)

        self.btn_new_mask.setText('New Mask')
        self.btn_save_mask.setText('Save Mask')

        self.btn_open.setText('Open File')
        self.btn_scale.setText('x 2')
        self.btn_next.setText('Next')

        # type buttons
        self.btn_type_river = QPushButton(self)
        self.btn_type_lake = QPushButton(self)
        self.btn_type_road = QPushButton(self)
        self.btn_type_building = QPushButton(self)
        self.btn_type_firebreak = QPushButton(self)
        self.btn_type_cloud = QPushButton(self)
        self.btn_type_shade = QPushButton(self)

        self.type_btns = (self.btn_type_river, self.btn_type_lake,
                        self.btn_type_road, self.btn_type_building, 
                        self.btn_type_firebreak, self.btn_type_cloud,
                        self.btn_type_shade)

        self.btn_type_river.setText('River')
        self.btn_type_lake.setText('Lake')
        self.btn_type_road.setText('Road')
        self.btn_type_building.setText('Building')
        self.btn_type_firebreak.setText('Firebrk')
        self.btn_type_cloud.setText('Cloud')
        self.btn_type_shade.setText('Shade')

        self.btn_type_river.setCheckable(True)

        #self.btn_type_river.toggle()
        self.btn_type_lake.setCheckable(True)
        self.btn_type_road.setCheckable(True)
        self.btn_type_building.setCheckable(True)
        self.btn_type_firebreak.setCheckable(True)
        self.btn_type_cloud.setCheckable(True)
        self.btn_type_shade.setCheckable(True)


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

        self.frm = QFrame(self)
        subgrid = QGridLayout()
        subgrid.addWidget(self.btn_type_river, 0, 0, Qt.AlignCenter)
        subgrid.addWidget(self.btn_type_lake, 0, 1, Qt.AlignCenter)
        subgrid.addWidget(self.btn_type_road, 1, 0, Qt.AlignCenter)
        subgrid.addWidget(self.btn_type_building, 1, 1, Qt.AlignCenter)
        subgrid.addWidget(self.btn_type_firebreak, 2, 0, Qt.AlignCenter)
        subgrid.addWidget(self.btn_type_cloud, 2, 1, Qt.AlignCenter)
        subgrid.addWidget(self.btn_type_shade, 3, 0, Qt.AlignCenter)
        self.frm.setLayout(subgrid)
        
        grid = QGridLayout()
        grid.addWidget(self.lbl, 0, 0, 5, 1, Qt.AlignCenter)
        grid.addWidget(self.sld, 5, 0, Qt.AlignCenter)

        grid.addWidget(self.btn_open, 0, 1, Qt.AlignVCenter)
        grid.addWidget(self.btn_new_mask, 1, 1, Qt.AlignVCenter)
        grid.addWidget(self.frm, 2, 1, Qt.AlignVCenter)
        grid.addWidget(self.btn_save_mask, 3, 1, Qt.AlignVCenter)
        grid.addWidget(self.btn_scale, 4, 1, Qt.AlignVCenter)
        grid.addWidget(self.btn_next, 5, 1, Qt.AlignVCenter)
        
        self.setLayout(grid)

        self.lbl.pressed.connect(self.magic_wand)
        # btn_open opens a dialogue for selecting a directory
        # containing the images to label.
        self.btn_open.pressed.connect(self.showDialog)
        self.btn_scale.pressed.connect(lambda: self.mark_as(1))
        # btn_next opens the next image from the directory.
        self.btn_next.pressed.connect(self.clear_tile_cash)
        self.btn_next.pressed.connect(self.open_file)
        # sld controls the FloodFill threshold value
        self.sld.valueChanged.connect(self.change_thresh)
        #
        self.btn_scale.pressed.connect(self.x2)
        #
        self._save_flag = 0
        self.btn_next.pressed.connect(self.save_mask)
        #
        self.btn_type_river.pressed.connect(self.btn_checked)
        self.btn_type_lake.pressed.connect(self.btn_checked)
        self.btn_type_road.pressed.connect(self.btn_checked)
        self.btn_type_building.pressed.connect(self.btn_checked)
        self.btn_type_firebreak.pressed.connect(self.btn_checked)
        self.btn_type_cloud.pressed.connect(self.btn_checked)
        self.btn_type_shade.pressed.connect(self.btn_checked)
        #
        self.btn_new_mask.pressed.connect(self.create_mask_type)
        #
        self.btn_save_mask.pressed.connect(lambda: self.combine_masks(self._mask_type, self._mask))
        #
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

        self._ih = pixm.height() // self._y_scale
        self._iw = pixm.width() // self._x_scale

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

        # contours to represent the type mask
        contours_type, _ = cv2.findContours(self._mask_type[1:-1, 1:-1], cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        draw_type = cv2.drawContours(self.img.copy(), contours_type, -1, (0, 128, 128), 1)

        # contours to represent the current selection
        contours_selection, _ = cv2.findContours(self._mask[1:-1, 1:-1], cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        draw_selection = cv2.drawContours(draw_type.copy(), contours_selection, -1, (128, 128, 0), 1)
        # display both selections
        applied_mask_1 = QImage(draw_selection.data, draw_selection.shape[1], draw_selection.shape[0], draw_selection.strides[0], QImage.Format_RGB888)
        pixm = QPixmap(applied_mask_1)

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


    def save_mask(self):
        if self._save_flag == 0:
            self._save_flag = 1
        else:
            imwrite('name.bmp', self._mask*255, format='bmp')
            QImage(self._mask.data, self._mask.shape[1], self._mask.shape[0], self._mask.strides[0], QImage.Format_Mono).save('mask.bmp', format='bmp')

    def btn_checked(self):
        if self._toggled:
            self._toggled.toggle()
        self._toggled = self.sender()

    def mark_as(self, n):

        """ Add number corresponding to the surface type to an
        array associated with the opened image."""

        self.tile_cash.append(n)
        #print(self.tile_cash)

    def clear_tile_cash(self):

        """ Clear the surface obsects array associated with the 
        opened image. """

        self.tile_cash = []

    def combine_masks(self, mask_1, mask_2):
        # works in place (mask_1)
        mask_1 |= (mask_1 == 1) | (mask_2 == 1)
        plt.imshow(mask_1)
        plt.show()

    def subtract_masks(self, mask_1, mask_2):
        mask_1 = (mask_1 == 1) & (mask_2 == 0)

    def create_mask_type(self):
        self._mask_type = numpy.zeros((self._ih+2, self._iw+2), dtype=uint8)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = myGUI()
    sys.exit(app.exec_())