# Calibración de la webcam

Usa un tablero plano de **10 × 7 cuadrados**, que tiene **9 × 6 esquinas interiores**. Mide el lado de un cuadrado impreso en milímetros. Usa la misma webcam y resolución que utilizarás en Simón Dice.

## 1. Capturar las fotos

Selecciona el intérprete `voi-lab` en VS Code. Abre `calibrar.py` y pulsa **▶ Ejecutar archivo de Python**. Si ya tienes fotos, pulsa **Enter** para añadir más o escribe **C** y pulsa **Enter** para calibrar con las guardadas.

Cuando el programa encuentre el tablero, verás las esquinas marcadas sobre el vídeo. Pulsa **Espacio** para comprobar el tablero en el fotograma completo. Si se guarda, verás el nombre de la foto y aumentará el contador de fotos nuevas. Si se rechaza, la ventana te indicará el motivo. Captura unas **15–25 fotos** con el tablero en el centro, los bordes y las esquinas del encuadre. Varía la distancia y la inclinación. Pulsa **Q** o **Esc** para terminar. Las fotos se guardan en `calibracion/fotos/`.

La vista muestra la resolución real. Al añadir fotos, el script pide a la cámara la resolución de las guardadas. Para empezar una calibración con otra resolución, guarda las fotos anteriores en otra carpeta y cambia `RESOLUCION` al principio de `calibrar.py`. Si Windows no abre la cámara, puedes cambiar `INDICE_CAMARA` a `1` o `METODO_CAPTURA` a `cv2.CAP_DSHOW`.

## 2. Calibrar offline

Al cerrarse la ventana de captura, el script libera la webcam y te pide en la terminal el lado de un cuadrado. Escribe el valor en milímetros, por ejemplo `25`, y pulsa **Enter**. La calibración se calcula a partir de las fotos guardadas en `calibracion/fotos/`.

El resultado queda en `calibracion/parametros.json`. Para el informe, copia la **resolución**, la **matriz de cámara**, los **coeficientes de distorsión** y el **RMS global en píxeles**. También se guarda el RMS por foto para que puedas revisar las capturas con mayor error.
