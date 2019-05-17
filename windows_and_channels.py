import rasterio
from rasterio import windows
from matplotlib import pyplot as plt
from os import listdir
import cv2
import numpy as np
from pathlib import Path

def get_size_coefs(dirpath):

    # the directory should only contain image files
    # the files should be named uniformely according to the bands they represent
    # B01.jp2, B02.jp2 ...

    bands = listdir(dirpath)
    bands.sort()

    w = []
    h = []

    for band in bands:
        with rasterio.open(Path(dirpath, band)) as src:
            w.append(src.meta['width'])
            h.append(src.meta['height'])

    mw = max(w)
    mh = max(h)

    coef_w = [mw // item for item in w]
    coef_h = [mh // item for item in h]

    return coef_h, coef_w, mh, mw

def open_chosen_bands(dirpath, chosen_bands, size, position):

    # the directory should only contain 13 image files
    # representing bands sensed by sentinel-2
    # the files should be named according to the bands
    # they represent: B01.jp2, B02.jp2 ...

    bands = listdir(dirpath)
    bands.sort()
    bands = [Path(dirpath, band) for n, band in enumerate(bands)]

    # TODO: check image limits
    coef_h, coef_w, mh, mw = get_size_coefs(dirpath)
    
    tile_layers = []

    for band in chosen_bands:
        with rasterio.open(bands[band]) as src:
            # Size and position are set for the tile from the band with
            # the lowest resolution (among the chosen), thus the bands
            # with higher resolutoins have proportionally bigger tiles.
            img = src.read(1, window=windows.Window(\
                position[0] // coef_h[band], 
                position[1] // coef_w[band], 
                size[0] // coef_h[band], size[1] // coef_w[band]))
        # resize tiles to the size of the biggest tile
        img = cv2.resize(img, (img.shape[1]*coef_h[band], img.shape[0]*coef_w[band]))   
        resid_y = size[0] - img.shape[0]
    resid_x = size[1] - img.shape[1]
        img = np.pad(img, ((0, resid_y), (0, resid_x)), 'constant', constant_values=((0, 0), (0, 0)))
        tile_layers.append(img)
    return tile_layers

def NBR(tile_layers):
    # TODO: correctly handle negative values
    div1 = (tile_layers[0] - tile_layers[1])
    div2 = (tile_layers[0] + tile_layers[1])
    res = np.divide(div1, div2)
    return res

def equlalize_hist(input_image, percent=(0, 0)):

    output_image = input_image.copy()

    if len(output_image.shape) == 3:
        for channel in range(3):
            output_image[:,:,channel] = clip_hist(output_image[:,:,channel], percent)      
    elif len(output_image.shape) == 2:
        output_image = clip_hist(output_image, percent)

    output_image = output_image.astype(np.uint8)
    
    return output_image

def clip_hist(image, percent=(0, 0)):
    borders = np.percentile(image, (percent[0], 100 - percent[1]))
    image = (image - borders[0])*255/(borders[1] - borders[0])
    return image