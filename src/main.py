"""Ventana básica del núcleo: vídeo, acceso y partida en texto."""
import argparse
from collections import deque
from pathlib import Path
import sys
import time

import cv2

ROOT = Path(__file__).resolve().parents[1]
TITLE = "Simon dice | Esc: salir"



def label(image, text, line=0):
    text = text.encode("ascii", errors="replace").decode()
    at = (12, 28 + line * 30)
    cv2.putText(image, text, at, cv2.FONT_HERSHEY_SIMPLEX, .65, (0, 0, 0), 4)
    cv2.putText(image, text, at, cv2.FONT_HERSHEY_SIMPLEX, .65, (255, 255, 255), 1)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Simón dice con webcam")

    args = parser.parse_args(argv)
    camera = cv2.VideoCapture(0)
    try:
        while True:
            ok, image = camera.read()
            if not ok:
                raise RuntimeError("No se reciben imágenes de la webcam.")

            cv2.imshow(TITLE, image)
            key = cv2.waitKey(1) & 255
            if key in (27, ord("q")) or cv2.getWindowProperty(TITLE, cv2.WND_PROP_VISIBLE) < 1:
                return 0

    except (RuntimeError, cv2.error) as error:
        print(error, file=sys.stderr)
        return 1
    finally:
        camera.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    raise SystemExit(main())
