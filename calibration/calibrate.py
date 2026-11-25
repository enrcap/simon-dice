"""Captura el tablero y calcula la calibración después de cerrar la webcam."""

import argparse
from datetime import datetime
import json
import math
from pathlib import Path
import sys
from tempfile import NamedTemporaryFile

import cv2
import numpy as np


CARPETA = Path(__file__).resolve().parent
PATRON = (9, 6)  # Esquinas interiores del tablero de 10 × 7 cuadrados.
RESOLUCION = (1280, 720)
EXTENSIONES = {".jpg", ".jpeg", ".png", ".bmp"}
CRITERIO = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_MAX_ITER, 30, 0.01)


def detectar_esquinas(gris, en_directo=False):
    flags = cv2.CALIB_CB_ADAPTIVE_THRESH | cv2.CALIB_CB_NORMALIZE_IMAGE
    if en_directo:
        flags |= cv2.CALIB_CB_FAST_CHECK
    encontrado, esquinas = cv2.findChessboardCorners(gris, PATRON, flags)
    if encontrado:
        return cv2.cornerSubPix(gris, esquinas, (5, 5), (-1, -1), CRITERIO)
    return None


def leer_gris(ruta):
    datos = np.fromfile(ruta, dtype=np.uint8)
    return cv2.imdecode(datos, cv2.IMREAD_GRAYSCALE) if datos.size else None


def capturar(fotos_existentes, carpeta_fotos, indice_camara):
    resolucion_fotos = None
    for ruta in fotos_existentes:
        gris = leer_gris(ruta)
        if gris is not None:
            resolucion_fotos = gris.shape[::-1]
            break
    ancho_solicitado, alto_solicitado = resolucion_fotos or RESOLUCION
    metodos = (cv2.CAP_MSMF, cv2.CAP_DSHOW) if sys.platform == "win32" else (cv2.CAP_ANY,)
    for metodo in metodos:
        camara = cv2.VideoCapture(indice_camara, metodo)
        if camara.isOpened():
            break
        camara.release()
    ventana = "Captura de calibracion"
    guardadas = 0
    ventana_abierta = False
    aviso = "ESPACIO: guardar | Q o Esc: terminar"

    try:
        if not camara.isOpened():
            raise ValueError(
                f"No se pudo abrir la cámara {indice_camara}. "
                "Comprueba el índice y cierra otros programas que estén usando la cámara."
            )
        camara.set(cv2.CAP_PROP_FRAME_WIDTH, ancho_solicitado)
        camara.set(cv2.CAP_PROP_FRAME_HEIGHT, alto_solicitado)
        carpeta_fotos.mkdir(parents=True, exist_ok=True)
        cv2.namedWindow(ventana, cv2.WINDOW_NORMAL)
        ventana_abierta = True

        while True:
            recibido, imagen = camara.read()
            if not recibido:
                raise ValueError("La cámara dejó de entregar fotogramas.")

            alto, ancho = imagen.shape[:2]
            gris_original = cv2.cvtColor(imagen, cv2.COLOR_BGR2GRAY)
            # Reducir solo la imagen que se analiza en la vista en directo.
            escala = min(1.0, 640 / max(ancho, alto))
            gris = gris_original
            if escala < 1:
                gris = cv2.resize(gris, None, fx=escala, fy=escala, interpolation=cv2.INTER_AREA)
            esquinas = detectar_esquinas(gris, en_directo=True)
            vista = imagen.copy()
            estado = "Buscando tablero"
            if esquinas is not None:
                escala_xy = (ancho / gris.shape[1], alto / gris.shape[0])
                esquinas_vista = (esquinas * escala_xy).astype(np.float32)
                cv2.drawChessboardCorners(vista, PATRON, esquinas_vista, True)
                estado = "Tablero detectado"

            lineas = (
                f"{ancho}x{alto} | {len(fotos_existentes) + guardadas} fotos ({guardadas} nuevas)",
                f"{estado} | ESPACIO: guardar | Q: terminar",
                aviso,
            )
            for y, texto in zip((26, 50, 74), lineas):
                cv2.putText(vista, texto, (12, y), cv2.FONT_HERSHEY_SIMPLEX,
                            0.55, (0, 0, 0), 4, cv2.LINE_AA)
                cv2.putText(vista, texto, (12, y), cv2.FONT_HERSHEY_SIMPLEX,
                            0.55, (255, 255, 255), 1, cv2.LINE_AA)
            cv2.imshow(ventana, vista)

            tecla = cv2.waitKey(1) & 0xFF
            if tecla in (ord("q"), 27) or cv2.getWindowProperty(ventana, cv2.WND_PROP_VISIBLE) < 1:
                break
            if tecla != ord(" "):
                continue
            if resolucion_fotos is not None and (ancho, alto) != resolucion_fotos:
                anterior = f"{resolucion_fotos[0]}x{resolucion_fotos[1]}"
                aviso = f"No guardada: las fotos anteriores son de {anterior}"
                print(f"{aviso} y la cámara entrega {ancho}x{alto}.")
                continue
            if detectar_esquinas(gris_original) is None:
                aviso = "No guardada: muestra el tablero entero y mantenlo quieto"
                print(aviso)
                continue

            nombre = datetime.now().strftime("tablero_%Y%m%d_%H%M%S_%f.png")
            guardado, datos = cv2.imencode(".png", imagen)
            if not guardado:
                raise ValueError("No se pudo codificar la foto.")
            with (carpeta_fotos / nombre).open("xb") as archivo:
                archivo.write(datos.tobytes())
            resolucion_fotos = (ancho, alto)
            guardadas += 1
            aviso = "Foto guardada. Cambia la inclinacion o posicion del tablero."
            print(aviso)
    finally:
        camara.release()
        if ventana_abierta:
            cv2.destroyAllWindows()

    print(f"{guardadas} fotos nuevas guardadas en {carpeta_fotos}")


def listar_fotos(carpeta_fotos):
    if not carpeta_fotos.is_dir():
        return []
    return sorted(
        ruta for ruta in carpeta_fotos.iterdir()
        if ruta.is_file() and ruta.suffix.lower() in EXTENSIONES
    )

def main():
    parser = argparse.ArgumentParser(description="Capturar vistas del tablero.")
    parser.add_argument("--camara", type=int, default=0)
    args = parser.parse_args()
    folder = CARPETA / "fotos" / f"camara_{args.camara}"
    capturar(listar_fotos(folder), folder, args.camara)


if __name__ == "__main__":
    main()
