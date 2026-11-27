import cv2
import numpy as np


def rectificar(region, puntos):
    destino = np.float32([[0, 0], [99, 0], [99, 99], [0, 99]])
    matriz = cv2.getPerspectiveTransform(puntos, destino)
    return cv2.warpPerspective(region, matriz, (100, 100))


def _ordenar_esquinas(cuadrado):
    # Orden circular: arriba izquierda, arriba derecha, abajo derecha e izquierda.
    puntos = cuadrado.reshape(4, 2).astype(np.float32)
    centro = puntos.mean(axis=0)
    angulos = np.arctan2(puntos[:, 1] - centro[1], puntos[:, 0] - centro[0])
    puntos = puntos[np.argsort(angulos)]
    primero = np.argmin(puntos.sum(axis=1))
    return np.roll(puntos, -primero, axis=0)
