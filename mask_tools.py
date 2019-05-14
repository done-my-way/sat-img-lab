import numpy as np
import cv2
import imageio
from matplotlib import pyplot as plt
from pathlib import Path
import os

# check masks directory: are there any masks to work on (proceed the work on)?
def check_masks(dir_path):
    if not os.path.isdir(dir_path):
        os.mkdir(dir_path)
    masks = os.listdir(dir_path)
    return masks

# create mask: stored - on the disk, size - biggest band + mirroring
## an array (10000 x 10000, uint8) saved with the np.save is about 85 Mb
def create_mask(file_name, dir_path, size):
    if not file_name in check_masks(dir_path):
        mask = np.zeros(size, dtype=np.uint8)
        np.save(Path(dir_path, file_name), mask)
# 
def open_mask(file_name):
    mask = np.load(file_name, mmap_mode='r+')
    return mask

# load mask: consider memmap

def load_mask_tile(mask, pos, size):
    mask_tile = mask[pos[0]:pos[0] + size[0], pos[1]:pos[1] + size[1]]
    return mask_tile.copy()

# save mask: consider memmap
def save_mask_tile(mask, tile, pos, size):
    mask[pos[0]:pos[0] + size[0], pos[1]:pos[1] + size[1]] = tile.copy()
    return None

# layer mask over an image: alpha? (layers in PyQy.Image? or cv2)
# better contours than opacity?
# chessboard
def mask_image(image, mask, alpha=0.1):
    src2 = np.zeros(image.shape)
    for i in range(2):
        src2[:, :, i] = mask
    # blend
    beta = 1.0 - alpha
    masked = image * alpha + image * src2 * beta
    masked = masked.astype(np.uint8)
    # overlay

    return masked

if __name__ == '__main__':
    # test it 1
    # create_mask('./masks/mask.npy', (10900, 10900))
    # mask = open_mask('./masks/mask.npy')
    # size = (10, 10)
    # position = (1000, 1000)
    # tile = np.full(size, 27)
    # temp1 = load_mask(mask, position, size)
    # print(temp1)
    # save_mask(mask, tile, position, size)
    # temp2  = load_mask(mask, position, size)    
    # print(temp2)

    # test it 2
    image = imageio.imread('./tiles_sat/00.jp2')
    image = image.astype(np.uint8)
    mask = np.full((256, 256), 1, dtype = np.uint8)
    lx, ly = mask.shape
    X, Y = np.ogrid[0:lx, 0:ly]
    circle = (X - lx / 2) ** 2 + (Y - ly / 2) ** 2 > lx * ly / 4
    mask[circle] = 0
    print(image.dtype, mask.dtype)
    masked = mask_image(image, mask)
    plt.imshow(masked)
    plt.show()
