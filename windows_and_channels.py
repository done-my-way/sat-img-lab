import rasterio
from rasterio import windows
from matplotlib import pyplot as plt
from os import listdir
import cv2
import numpy as np
from pathlib import Path

# path = '/home/lodya/Desktop/DigDes/sat-img-lab/bands'
# bands = listdir(path)
# bands.sort()
# window_size_max = 216

# w = []
# h = []

# for band in bands:
#     with rasterio.open(path+'/'+band) as src:
#         w.append(src.meta['width'])
#         h.append(src.meta['height'])

# print(w)
# max_w = max(w)
# max_h = max(h)

# coefs_w = [max_w//i for i in w]
# coefs_h = [max_h//i for i in h]

# tile_layers = []
# i = 0
# for i in [7, 10, 4]:
#     with rasterio.open(path+'/'+bands[i]) as src:

#         img = src.read(1, window=windows.Window(0, 0, window_size_max*6/coefs_w[i], window_size_max*6/coefs_w[i]))
#         print(img.shape)
#         img = img / np.amax(img) * 255        
#         img = img.astype(np.uint8)
#         tile_layers.append(img)

# size = max([im.shape[0] for im in tile_layers])
# tile_layers = [cv2.resize(im, (size, size)) for im in tile_layers]
# tile_layers = np.hstack(tile_layers)
# # plt.imshow(tile_layers)
# # plt.show()
# print(tile_layers.shape)
# a = tile_layers.shape[0]
# new_img = np.zeros((a, a, 3), dtype = np.uint8)

# new_img[:,:,2] = tile_layers[:,0:a]
# new_img[:,:,1] = tile_layers[:,a:2*a]
# new_img[:,:,0] = tile_layers[:, 2*a:3*a]
# print(np.amax(new_img))
# print(new_img.shape)
# plt.imshow(new_img)
# plt.show()

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
    print(min_w)
    size_coefs = [(all_sizes[band][0]//min_w, all_sizes[band][1]//min_h) for band in chosen_bands]
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

def assemble_multi_channel(tile_layers):
    for img in tile_layers:
        img = img / np.amax(img) * 255        
        img = img.astype(np.uint8)

if __name__ == "__main__":

    dirpath = '/home/lodya/Desktop/DigDes/sat-img-lab/bands'

    bands, sizes = open_image(dirpath)

    print(bands, '\n', sizes)
    
    tile_layers = open_tile((1, 2, 3), bands, sizes, (100, 100), (0, 0))

    for layer in tile_layers:
        plt.imshow(layer)
        plt.show()
    