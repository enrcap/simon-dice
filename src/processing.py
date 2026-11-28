"""Funciones reutilizadas de los cuadernos de Visión por Ordenador I.

Lab/lab_3/src/partA-B.ipynb: gaussian_blur (A.1), binarize (B.1),
custom_dilate (B.2) y custom_erode (B.3). Se conservan sus operaciones
NumPy y sus bucles. Se eliminan las opciones de gráficos del cuaderno.
"""
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

def custom_dilate(img):
    # TODO pad the original image so it can keep dimensions after processing
    padded = np.pad(img, 1, mode="constant", constant_values=0)

    # TODO get img shape
    height, width = img.shape

    # TODO Create an element with the same dimensions as the padded img
    dilated = np.zeros(padded.shape, dtype=np.uint8)
    kernel = np.ones((3, 3), dtype=np.uint8)*255

    for j in range(height):
        for i in range(width):
            # Si hay un píxel blanco en la ventana, el resultado es blanco
            region = padded[j:j+3, i:i+3]
            dilated[j+1, i+1] = np.max(region[kernel == 255])

    # TODO Select the region of interest (ROI). Modify if needed
    dilated = dilated[1:height+1, 1:width+1]

    return dilated

def custom_erode(img):
    padded = np.pad(img, 1, mode="constant", constant_values=0)
    height, width = img.shape
    eroded = np.zeros(padded.shape, dtype=np.uint8)
    kernel = np.ones((3, 3), dtype=np.uint8)*255

    for j in range(height):
        for i in range(width):
            # El resultado es blanco solo si todos los píxeles son blancos
            region = padded[j:j+3, i:i+3]
            eroded[j+1, i+1] = np.min(region[kernel == 255])

    eroded = eroded[1:height+1, 1:width+1]
    return eroded


def zona_tarjeta(frame):
    """Zona central para presentar una tarjeta completa con su margen blanco."""
    alto, ancho = frame.shape[:2]
    lado = int(0.68 * min(alto, ancho))
    x = (ancho - lado) // 2
    y = (alto - lado) // 2
    return x, y, x + lado, y + lado

def candidatos_marco(frame):
    x1, y1, x2, y2 = zona_tarjeta(frame)
    region = frame[y1:y2, x1:x2]
    gris = cv2.cvtColor(region, cv2.COLOR_BGR2GRAY)
    _, gris = gaussian_blur(gris, sigma=.8, filter_shape=[3, 3])
    bordes = cv2.Canny(gris, 50, 150)
    contornos, _ = cv2.findContours(bordes, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    for contorno in contornos:
        if cv2.contourArea(contorno) < .018 * gris.size:
            continue
        perimetro = cv2.arcLength(contorno, True)
        cuadrado = cv2.approxPolyDP(contorno, .035 * perimetro, True)
        if len(cuadrado) == 4 and cv2.isContourConvex(cuadrado):
            yield region, cuadrado, (x1, y1)
