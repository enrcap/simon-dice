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


def calibrar(fotos, cuadrado_mm, archivo_parametros, indice_camara):
    if not math.isfinite(cuadrado_mm) or cuadrado_mm <= 0:
        raise ValueError("El lado del cuadrado debe ser un número positivo en milímetros.")

    columnas, filas = PATRON
    puntos_tablero = np.array(
        [(columna * cuadrado_mm, fila * cuadrado_mm, 0)
         for fila in range(filas) for columna in range(columnas)],
        dtype=np.float32,
    )

    resolucion = None
    puntos_imagen = []
    usadas = []
    for ruta in fotos:
        gris = leer_gris(ruta)
        if gris is None:
            print(f"Descartada {ruta.name}: imagen ilegible.")
            continue
        esquinas = detectar_esquinas(gris)
        if esquinas is None:
            print(f"Descartada {ruta.name}: tablero no detectado.")
            continue
        alto, ancho = gris.shape
        if resolucion is None:
            resolucion = (ancho, alto)
        elif (ancho, alto) != resolucion:
            raise ValueError(f"{ruta.name} mide {ancho}x{alto}. Usa fotos de una sola resolución.")
        puntos_imagen.append(esquinas)
        usadas.append(ruta.name)

    if len(usadas) < 3:
        raise ValueError(
            f"Solo se detectó el tablero en {len(usadas)} fotos. "
            "Captura más vistas con distintas posiciones e inclinaciones."
        )

    rms, matriz, distorsion, rotaciones, traslaciones = cv2.calibrateCamera(
        [puntos_tablero] * len(usadas), puntos_imagen, resolucion, None, None
    )
    if not math.isfinite(rms) or not np.isfinite(matriz).all() or not np.isfinite(distorsion).all():
        raise ValueError("La calibración no dio valores finitos. Captura vistas más variadas.")

    errores = {}
    for nombre, esquinas, rotacion, traslacion in zip(
        usadas, puntos_imagen, rotaciones, traslaciones
    ):
        proyectadas, _ = cv2.projectPoints(
            puntos_tablero, rotacion, traslacion, matriz, distorsion
        )
        diferencia = (esquinas - proyectadas).reshape(-1, 2)
        errores[nombre] = float(np.sqrt(np.mean(np.sum(diferencia ** 2, axis=1))))

    resultado = {
        "indice_camara": indice_camara,
        "resolucion": list(resolucion),
        "esquinas_interiores": list(PATRON),
        "lado_cuadrado_mm": cuadrado_mm,
        "matriz_camara": matriz.tolist(),
        "coeficientes_distorsion": distorsion.ravel().tolist(),
        "rms_px": float(rms),
        "numero_fotos": len(usadas),
        "rms_por_foto_px": errores,
    }
    temporal = None
    try:
        with NamedTemporaryFile(mode="w", encoding="utf-8", dir=archivo_parametros.parent,
                                prefix="parametros_", suffix=".tmp", delete=False) as salida:
            temporal = Path(salida.name)
            json.dump(resultado, salida, indent=2, ensure_ascii=False)
            salida.write("\n")
        temporal.replace(archivo_parametros)
    finally:
        if temporal is not None:
            temporal.unlink(missing_ok=True)
    print(f"Resolución: {resolucion[0]}x{resolucion[1]} | Fotos válidas: {len(usadas)}")
    print(f"RMS global: {rms:.4f} px")
    print(f"Matriz de cámara:\n{matriz}")
    print(f"Coeficientes de distorsión: {distorsion.ravel()}")
    print(f"Parámetros guardados en {archivo_parametros}")


def main(argv=None, *, directory=None):
    parser = argparse.ArgumentParser(description="Calibra la webcam con un tablero de ajedrez.")
    parser.add_argument("--camara", type=int, default=0, choices=range(10), metavar="N")
    parser.add_argument("--solo-fotos", action="store_true", help="Usa las fotos existentes sin abrir la webcam.")
    parser.add_argument("--lado-mm", help="Lado de una casilla impresa, en milímetros.")
    args = parser.parse_args(argv)
    directorio = Path(directory) if directory is not None else CARPETA
    archivo_parametros = directorio / "parametros.json"
    carpeta_fotos = directorio / "fotos" / f"camara_{args.camara}"
    try:
        medida = args.lado_mm
        if medida is None:
            medida = input("¿Cuánto mide el lado de un cuadrado del tablero en mm? ").strip()
        try:
            cuadrado_mm = float(medida.replace(",", "."))
        except ValueError:
            raise ValueError("Introduce solo la medida en milímetros, por ejemplo 25 o 25,5.") from None
        if not math.isfinite(cuadrado_mm) or cuadrado_mm <= 0:
            raise ValueError("El lado del cuadrado debe ser un número positivo en milímetros.")
        fotos = listar_fotos(carpeta_fotos)
        if not args.solo_fotos:
            capturar(fotos, carpeta_fotos, args.camara)
            fotos = listar_fotos(carpeta_fotos)
        if not fotos:
            raise ValueError("No hay fotos del tablero para calibrar.")
        print(f"Se revisarán {len(fotos)} fotos de {carpeta_fotos}.")
        calibrar(fotos, cuadrado_mm, archivo_parametros, args.camara)
    except EOFError:
        print("Ejecuta el script desde la terminal de VS Code.", file=sys.stderr)
        return 1
    except (ValueError, OSError, cv2.error) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
