import rasterio
from rasterio import windows
from matplotlib import pyplot as plt
from os import listdir
import cv2
import numpy as np
from pathlib import Path


def open_image(dirpath):
    # the directory should only contain image files
    # the files should be named uniformely according to the bands they represent
    # B01.jp2, B02.jp2 ...
    bands = listdir(dirpath)
    bands.sort()
    bands = [Path(dirpath, band) for band in bands]
    sizes = []
    for band in bands:
        with rasterio.open(band) as src:
                sizes.append((src.meta['width'], src.meta['height']))
    return bands, sizes


def open_tile(chosen_bands, all_bands, all_sizes, size, position):
    # TODO: check image limits
    min_w = min(all_sizes, key=lambda x: x[0])[0]
    min_h = min(all_sizes, key=lambda x: x[1])[0]
    size_coefs = [(all_sizes[band][0]//min_w, all_sizes[band][1]//min_h) for band in range(len(all_sizes))]
    #
    tile_layers = []
    for band in chosen_bands:
        with rasterio.open(all_bands[band]) as src:
            img = src.read(1, window=windows.Window(\
                position[0] * size_coefs[band][0], 
                position[1] * size_coefs[band][1], 
                size[0] * size_coefs[band][0], size[1] * size_coefs[band][1]))
        tile_layers.append(img)
    return tile_layers

def open_chosen_bands(dirpath, chosen_bands, size, position):

    # the directory should only contain 13 image files
    # representing bands sensed by sentinel-2
    # the files should be named according to the bands
    # they represent: B01.jp2, B02.jp2 ...

    bands = listdir(dirpath)
    bands.sort()
    bands = [Path(dirpath, band) for n, band in enumerate(bands) if n in chosen_bands]
    w = []
    h = []
    for band in bands:
        with rasterio.open(band) as src:
            w.append(src.meta['width'])
            h.append(src.meta['height'])
    # TODO: check image limits
    size_coefs = [(ww//min(w), hh//min(h)) for ww, hh in zip(w, h)]
    #
    tile_layers = []
    for i in range(len(chosen_bands)):
        with rasterio.open(bands[i]) as src:
            # Size and position are set for the tile from the band with
            # the lowest resolution (among the chosen), thus the bands
            # with higher resolutoins have proportionally bigger tiles.
            img = src.read(1, window=windows.Window(\
                position[0] * size_coefs[i][0], 
                position[1] * size_coefs[i][1], 
                size[0] * size_coefs[i][0], size[1] * size_coefs[i][1]))
        tile_layers.append(img)
    return tile_layers

def assemble_multi_channel(tile_layers):
    # resize tiles to the size of the biggest tile
    size = max([im.shape[0] for im in tile_layers])
    tile_layers = [cv2.resize(im, (size, size)) for im in tile_layers]
    tile_layers = np.hstack(tile_layers)
    # convert (3, a, a) to (a, a, 3)-shaped numpy-array
    a = tile_layers.shape[0]
    new_img = np.zeros((a, a, 3))
    new_img[:,:,2] = tile_layers[:,0:a]
    new_img[:,:,1] = tile_layers[:,a:2*a]
    new_img[:,:,0] = tile_layers[:, 2*a:3*a]
    return new_img

def to_uint8_rgb(image):
    # represent as uint8 RGB
    m = np.amax(image)
    image = image / m * 255
    image = image.astype(np.uint8)
    # show RGB-img
    plt.imshow(image)
    plt.show()

if __name__ == "__main__":

    dirpath = '/home/lodya/Desktop/DigDes/sat-img-lab/bands'

    tile_layers = open_chosen_bands(dirpath, (1, 2, 3), (256, 256), (500, 500))

    # bands, sizes = open_image(dirpath)

    
    # tile_layers = open_tile((1, 2, 3), bands, sizes, (256, 256), (500, 500))

    # for layer in tile_layers:
    #     plt.imshow(layer)
    #     plt.show()

    to_uint8_rgb(assemble_multi_channel(tile_layers))
    