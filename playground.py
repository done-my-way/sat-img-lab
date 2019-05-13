import numpy as np 
from matplotlib import pyplot

a = np.load('./masks/river.npy')

pyplot.imshow(a)
pyplot.show()