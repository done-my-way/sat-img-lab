from imageio import imread, imwrite

img = imread('/home/lodya/Desktop/DigDes/sat-img-lab/test/18.tif')

print(type(img[0][0][0]))

imwrite('test.jpg', img, format='jpg')