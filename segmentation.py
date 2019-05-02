import numpy as np
import imageio 
from matplotlib import pyplot as plt
from scipy import ndimage

img = imageio.imread('/home/lodya/Desktop/DigDes/sat-img-lab/tiles_sat/11.jp2')
img = img.astype(np.uint8)[:, :, 0]
print(img.shape)
sx = ndimage.sobel(img, axis=0, mode='constant')
sy = ndimage.sobel(img, axis=1, mode='constant')
sob = np.hypot(sx, sy) 
sob = sob / np.amax(sob)
sob = sob.astype(np.float32)
print(sob.dtype)
plt.imshow(sob)
plt.show()