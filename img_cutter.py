from imageio import imread, imwrite
import matplotlib.pyplot as plt
import numpy


class imgCutter:
    """ """
    def __init__(self, path):
        self.img = imread(path)

    def cut_image(self, width=200, height=200):
        self.rows = self.img.shape[0] // height + 1
        self.cols = self.img.shape[1] // width + 1
        self.parts = [[0 for i in range(self.cols)] for j in range(self.rows)]
        print(len(self.parts))
        for i in range(self.rows):
            for j in range(self.cols):
                self.parts[i][j] = self.img[i *200:(i+1)*200, j*200:(j+1)*200, :]
        print(len(self.parts))

    def show_image(self):
        plt.imshow(self.img)
        plt.show()

    def show_parts(self):
        fig = plt.figure(figsize=(self.rows, self.cols))
        for i in range(self.rows):
            for j in range(self.cols):
                num = i * self.cols + j + 1
                img = self.parts[i][j]
                fig.add_subplot(self.rows, self.cols, num)
                plt.imshow(img)
        plt.show()


im = imgCutter(
    '/home/lodya/Documents/DigDes/sat-img-lab/MOS_SK_GK4_250/MOS_SK_GK4_250.tif')
im.cut_image()
im.show_parts()
