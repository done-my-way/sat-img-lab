import numpy as np 
from matplotlib import pyplot

a = np.load('./masks/test_padding.npy')

pyplot.imshow(a)
pyplot.show()