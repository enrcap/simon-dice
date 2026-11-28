import cv2
import numpy as np


def gaussian_blur(img, sigma, filter_shape=None):
    # TODO If not given, compute the filter shape
    if filter_shape == None:
        filter_l = 2*int(np.ceil(4*sigma))+1
        filter_shape = [filter_l, filter_l]

    radius_y = filter_shape[0] // 2
    radius_x = filter_shape[1] // 2
    # TODO Create the filter coordinates matrices
    y, x = np.mgrid[-radius_y:radius_y+1, -radius_x:radius_x+1]

    # TODO Define the formula that goberns the filter
    formula = lambda i, j: 1/(2*np.pi*sigma**2) * np.exp(-(i**2+j**2)/(2*sigma**2))
    gaussian_filter = formula(y, x)
    gaussian_filter = gaussian_filter / gaussian_filter.sum()

    # TODO Process the image
    gb_img = cv2.filter2D(img, ddepth=-1, kernel=gaussian_filter)

    return gaussian_filter, gb_img.astype(np.uint8)


def binarize(img, threshold=127):
    if img.ndim == 3:
        gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    else:
        gray_img = img
    binary_img = np.where(gray_img > threshold, 255, 0).astype(np.uint8)
    return binary_img
