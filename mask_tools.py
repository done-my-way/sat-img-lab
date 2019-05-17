import numpy as np

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
