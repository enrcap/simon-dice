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
    parser.add_argument("--camera", type=int, default=0, choices=range(10))
    parser.add_argument("--sin-espejo", action="store_true")
    args = parser.parse_args(argv)
    from .camera_open import open_camera
    camera = open_camera(args.camera)
    try:
        while True:
            ok, image = camera.read()
            if not ok:
                raise RuntimeError("No se reciben imágenes de la webcam.")
            if not args.sin_espejo:
                image = cv2.flip(image, 1)
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
