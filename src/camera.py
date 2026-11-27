"""Capture and inference workers; UI never waits for camera or model loading."""
from dataclasses import dataclass
import json
from pathlib import Path
import threading
import time

from .camera_open import open_camera


@dataclass
class FramePacket:
    image: object
    poses: list
    timestamp: float
    error: str = ""
    calibration_status: str = ""
    card_number: int | None = None
    card_contour: object = None
    pose_ready: bool = True





class CameraWorker:
    def __init__(self, camera: int, model_path: Path, players: int = 2, *,
                 calibration_path: Path | None = None, require_cards=False):
        self.camera = camera
        self.model_path = Path(model_path)
        self.players = players
        self.calibration_path = Path(calibration_path) if calibration_path is not None else None
        self._pose_allowed = threading.Event()
        self._pose_ready = threading.Event()
        if not require_cards:
            self._pose_allowed.set()
        self._stop = threading.Event()
        self._condition = threading.Condition()
        self._pending = None
        self._output = None
        self._threads = []

    def start(self):
        if self._threads:
            return
        self._stop.clear()
        self._threads = [threading.Thread(target=self._capture, daemon=True,
                                         name="SimonCapture")]
        for thread in self._threads:
            thread.start()

    def stop(self):
        self._stop.set()
        with self._condition:
            self._condition.notify_all()
        for thread in self._threads:
            thread.join(timeout=1.0)

    def latest(self) -> FramePacket | None:
        with self._condition:
            packet = self._output
            self._output = None
            return packet

    def allow_pose(self):
        self._pose_allowed.set()

    def _take_pending(self):
        with self._condition:
            self._condition.wait_for(lambda: self._pending is not None or self._stop.is_set(),
                                     timeout=0.25)
            if self._stop.is_set():
                return None
            pending, self._pending = self._pending, None
            return pending

    def _publish(self, packet):
        with self._condition:
            if not self._stop.is_set():
                if packet.pose_ready:
                    self._pose_ready.set()
                self._output = packet

    def _fail(self, message):
        with self._condition:
            self._output = FramePacket(None, [], time.monotonic(), message)
            self._stop.set()
            self._condition.notify_all()

    def _load_calibration(self):
        if self.calibration_path is None:
            return None, "Sin perfil de calibración óptica"
        try:
            record = json.loads(self.calibration_path.read_text(encoding="utf-8"))
            if not isinstance(record, dict):
                raise ValueError("el perfil no es un objeto JSON")
            return record, ""
        except FileNotFoundError:
            return None, "Sin perfil de calibración óptica"
        except (OSError, ValueError):
            return None, "No se pudo leer el perfil de calibración óptica"

    def _capture(self):
        camera = None
        try:
            import cv2
            camera = open_camera(self.camera)
            calibration, calibration_status = self._load_calibration()
            resolution = None
            maps = None
            while not self._stop.is_set():
                ok, frame = camera.read()
                captured_at = time.monotonic()
                if not ok or frame is None:
                    raise RuntimeError("Cámara desconectada o sin imagen")
                if calibration is not None and frame.shape[1::-1] != resolution:
                    resolution = frame.shape[1::-1]
                    try:
                        from calibration.profile import _calibration_maps
                        maps = _calibration_maps(calibration, self.camera, resolution)
                        calibration_status = "Calibración óptica aplicada"
                    except (TypeError, ValueError, cv2.error) as exc:
                        maps = None
                        calibration_status = f"Sin corrección óptica: {exc}"
                if maps is not None:
                    frame = cv2.remap(frame, *maps, cv2.INTER_LINEAR)
                with self._condition:
                    if self._stop.is_set():
                        break
                    self._pending = (frame, captured_at, calibration_status)
                    self._output = FramePacket(frame, [], captured_at,
                                               calibration_status=calibration_status, pose_ready=False)
                    self._condition.notify_all()
        except Exception as exc:
            self._fail(f"Cámara: {exc}")
        finally:
            if camera is not None:
                camera.release()




