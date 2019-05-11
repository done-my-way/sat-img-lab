import rasterio
from rasterio import windows
from matplotlib import pyplot as plt
from os import listdir
import cv2
import numpy as np
from pathlib import Path


def get_size_info(dirpath):
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
            print(img.shape)
        tile_layers.append(img)
    return tile_layers

def open_chosen_bands(dirpath, chosen_bands, size, position):

    # the directory should only contain 13 image files
    # representing bands sensed by sentinel-2
    # the files should be named according to the bands
    # they represent: B01.jp2, B02.jp2 ...

    print(position, size)

    bands = listdir(dirpath)
    w = []
    h = []
    for band in bands:
        with rasterio.open(Path(dirpath, band)) as src:
            w.append(src.meta['width'])
            h.append(src.meta['height'])

    mw = max(w)
    mh = max(h)

    bands.sort()
    bands = [Path(dirpath, band) for n, band in enumerate(bands) if n in chosen_bands]
    w = []
    h = []
    for band in bands:
        with rasterio.open(band) as src:
            w.append(src.meta['width'])
            h.append(src.meta['height'])
    # TODO: check image limits
    size_coefs = [(mw//ww, mh//hh) for ww, hh in zip(w, h)]
    #
    tile_layers = []
    for i in range(len(chosen_bands)):
        with rasterio.open(bands[i]) as src:
            # Size and position are set for the tile from the band with
            # the lowest resolution (among the chosen), thus the bands
            # with higher resolutoins have proportionally bigger tiles.
            img = src.read(1, window=windows.Window(\
                position[0] // size_coefs[i][0], 
                position[1] // size_coefs[i][1], 
                size[0] // size_coefs[i][0], size[1] // size_coefs[i][1]))
            print(img.shape)
        tile_layers.append(img)
    return tile_layers

def stack_three_channels(tile_layers):
    # resize tiles to the size of the biggest tile
    size_x = max([im.shape[1] for im in tile_layers])
    size_y = max([im.shape[0] for im in tile_layers])
    tile_layers = [cv2.resize(im, (size_x, size_y)) for im in tile_layers]
    tile_layers = np.hstack(tile_layers)
    # convert (3, a, a) to (a, a, 3)-shaped numpy-array
    a = tile_layers.shape[0]
    b = tile_layers.shape[1] // 3
    new_img = np.zeros((a, b, 3))
    new_img[:,:,2] = tile_layers[:,0:b]
    new_img[:,:,1] = tile_layers[:,b:2*b]
    new_img[:,:,0] = tile_layers[:, 2*b:3*b]
    # print(new_img.dtype)
    return new_img

def NBR(tile_layers):
    # TODO: correctly handle negative values
    size = max([im.shape[0] for im in tile_layers])
    tile_layers = [cv2.resize(im, (size, size)) for im in tile_layers]
    div1 = (tile_layers[0] - tile_layers[1])
    div2 = (tile_layers[0] + tile_layers[1])
    res = np.divide(div1, div2)
    # print(np.any(res < 0))
    return res

def to_uint8(input_image):

    output_image = input_image.copy()

    if len(output_image.shape) == 3:
        for channel in range(3):
            output_image[:,:,channel] = clip_hist(output_image[:,:,channel], (0, 0))      
    elif len(output_image.shape) == 2:
        output_image = clip_hist(output_image, (0, 0))
    output_image = output_image.astype(np.uint8)
    
    return output_image

def equlalize_hist(input_image):

    output_image = input_image.copy()

    if len(output_image.shape) == 3:
        # m = image.max()
        # color = ('b','g','r')
        for channel in range(3):
            # ma = image[:,:,channel].max()
            # mi = image[:,:,channel].min() # * 0.5
            # image[:,:,channel] = (image[:,:,channel] - mi) * 255 / (ma - mi)
            output_image[:,:,channel] = clip_hist(output_image[:,:,channel])
        
        # for i,col in enumerate(color):
        #     histr = cv2.calcHist([image],[i],None,[256],[0,256])
        #     plt.plot(histr,color = col)
        #     plt.xlim([0,256])
        # plt.show()        
    elif len(output_image.shape) == 2:
        output_image = clip_hist(output_image)
        # image = (image - image.min())*255/(image.max() - image.min())
        # image = np.ma.filled(image,0).astype('uint8')
        # histr = cv2.calcHist([image],[0],None,[256],[0,256])
        # plt.plot(histr)
        # plt.xlim([0,256])
        # plt.show()
    output_image = output_image.astype(np.uint8)
    
    return output_image

def clip_hist(image, percent=(0, 0)):
    borders = np.percentile(image, (percent[0], 100 - percent[1]))
    # print(borders)
    image = (image - borders[0])*255/(borders[1] - borders[0])
    # image = np.ma.filled(image,0).astype('uint8')
    return image


if __name__ == "__main__":

    dirpath = '/home/lodya/Desktop/DigDes/sat-img-lab/bands'

    tile_layers = open_chosen_bands(dirpath, (1, 2, 3), (256, 256), (500, 500))

    # bands, sizes = get_size_info(dirpath)

    
    # tile_layers = open_tile((1, 2, 3), bands, sizes, (256, 256), (500, 500))

    # for layer in tile_layers:
    #     plt.imshow(layer)
    #     plt.show()

    to_uint8_rgb(assemble_multi_channel(tile_layers))
    