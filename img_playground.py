from imageio import imread, imwrite
import matplotlib.pyplot as plt
import os
from pathlib import Path

def show_dir(dir_path):
    imgs = os.listdir(dir_path)
    i = 0
    for img in imgs:
        print(i)
        try:
            plt.figure(i)
            img = imread(Path(dir_path, img))
            plt.imshow(img)
            i += 1
        except Exception:
            pass
    plt.show()
    
show_dir('/home/lodya/Desktop/satellite')