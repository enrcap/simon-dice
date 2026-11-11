# Proyecto de Visión por Ordenador I

Primer objetivo: comprobar que la webcam devuelve vídeo en directo con el script de prueba del laboratorio.

## Probar la cámara en este equipo

En PowerShell, desde esta carpeta, usa el entorno de Python de las prácticas, que ya incluye OpenCV:

```powershell
& "$env:USERPROFILE\miniconda3\envs\voi-lab\python.exe" -c "from test import main; main(camera_index=0)"
```

Si no aparece el vídeo, prueba con el índice 1 ejecutando `& "$env:USERPROFILE\miniconda3\envs\voi-lab\python.exe" test.py`. Pulsa **Q** o **Esc** en la ventana de vídeo para salir.

## Preparar el entorno en otro equipo

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -c "from test import main; main(camera_index=0)"
```

## Siguientes pasos

- Elegir qué objeto o zona seguirá la cámara y concretar la propuesta.
- Calibrar la webcam con un patrón y guardar los parámetros y el error RMS.
- Detectar tarjetas y validar una secuencia de hasta cuatro patrones para desbloquear el seguimiento.
- Mostrar el rectángulo de seguimiento y los FPS sobre el vídeo.
