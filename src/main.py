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
    from .camera import CameraWorker
    profile = ROOT / "calibration" / "parametros.json"
    model = ROOT / "models" / "pose_landmarker_full.task"
    mirror = not args.sin_espejo
    camera = CameraWorker(args.camera, model, calibration_path=profile)
    stamps = deque(maxlen=30)
    camera.start()
    last_image = None
    last_received = time.monotonic()
    try:
        while True:
            packet = camera.latest()
            if packet is not None and packet.error:
                raise RuntimeError(packet.error)
            if packet is not None:
                last_received = time.monotonic()
                last_image = packet.image
                stamps.append(packet.timestamp)
            if time.monotonic() - last_received > 20:
                raise RuntimeError("No llegan imágenes recientes de la webcam.")
            if last_image is None:
                time.sleep(.01)
                continue
            image = last_image.copy()
            if mirror:
                image = cv2.flip(image, 1)
            if len(stamps) > 1 and stamps[-1] > stamps[0]:
                label(image, f"FPS {(len(stamps) - 1) / (stamps[-1] - stamps[0]):.1f}")
            cv2.imshow(TITLE, image)
            key = cv2.waitKey(1) & 255
            if key in (27, ord("q")) or cv2.getWindowProperty(TITLE, cv2.WND_PROP_VISIBLE) < 1:
                return 0

    except (RuntimeError, cv2.error) as error:
        print(error, file=sys.stderr)
        return 1
    finally:
        camera.stop()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    raise SystemExit(main())
