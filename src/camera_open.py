import cv2
import sys


def open_camera(index):
    backends = [cv2.CAP_MSMF, cv2.CAP_DSHOW] if sys.platform == "win32" else [cv2.CAP_ANY]
    for backend in backends:
        camera = cv2.VideoCapture(index, backend)
        if camera.isOpened():
            camera.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
            camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
            camera.set(cv2.CAP_PROP_BUFFERSIZE, 1)
            return camera
        camera.release()
    raise RuntimeError("No se puede abrir la cámara. Revisa el índice y los permisos.")
