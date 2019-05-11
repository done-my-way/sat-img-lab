import numpy as np
import cv2
import imageio
from matplotlib import pyplot as plt 

# check masks directory: are there any masks to work on (proceed the work on)?

# create mask: stored - on the disk, size - biggest band + mirroring
## an array (10000 x 10000, uint8) saved with the np.save is about 85 Mb
def create_mask(filename, size):
    mask = np.zeros(size, dtype=np.uint8)
    np.save(filename, mask)
# 
def open_mask(filename):
    mask = np.load(filename, mmap_mode='r+')
    return mask

# load mask: consider memmap
def load_mask(mask, pos, size):
    mask_tile = mask[pos[0]:pos[0] + size[0], pos[1]:pos[1] + size[1]]
    return mask_tile

# save mask: consider memmap
def save_mask(mask, tile, pos, size):
    mask[pos[0]:pos[0] + size[0], pos[1]:pos[1] + size[1]] = tile.copy()
    return None

# layer mask over an image: alpha? (layers in PyQy.Image? or cv2)
# better contours than opacity?
def mask_image(image, mask, alpha=0.8):
    src1 = image
    src2 = np.zeros(src1.shape)
    for i in range(2):
        src2[:, :, i] = mask
    plt.imshow(src2)
    plt.show()
    beta = 1.0 - alpha
    masked = src1 * alpha + src1 * src2 * beta
    masked = masked.astype(np.uint8)
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
    plt.imshow(image)
    plt.show()
    mask = np.full((256, 256), 1, dtype = np.uint8)
    lx, ly = mask.shape
    X, Y = np.ogrid[0:lx, 0:ly]
    circle = (X - lx / 2) ** 2 + (Y - ly / 2) ** 2 > lx * ly / 4
    mask[circle] = 0
    plt.imshow(mask)
    plt.show()
    print(image.dtype, mask.dtype)
    masked = mask_image(image, mask)
    plt.imshow(masked)
    plt.show()
