import numpy as np 
from matplotlib import pyplot

a = np.load('./masks/cloud.npy')

pyplot.imshow(a)
pyplot.show()