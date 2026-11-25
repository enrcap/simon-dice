def _calibration_maps(calibration, camera, resolution):
    """Compute remap tables in the coordinate space of the captured frame."""
    import cv2
    import numpy as np

    if calibration.get("indice_camara", 0) != camera:
        raise ValueError("el perfil corresponde a otra cámara")
    reference = calibration.get("resolucion")
    if (not isinstance(reference, list) or len(reference) != 2
            or any(type(extent) is not int or extent <= 0 for extent in reference)):
        raise ValueError("la resolución del perfil no es válida")
    width, height = resolution
    reference_width, reference_height = reference
    if width * reference_height != height * reference_width:
        raise ValueError("la cámara entrega un formato distinto al calibrado")
    matrix = np.asarray(calibration.get("matriz_camara"), dtype=np.float64)
    distortion = np.asarray(calibration.get("coeficientes_distorsion"), dtype=np.float64)
    if (matrix.shape != (3, 3) or not np.allclose(matrix[2], (0, 0, 1))
            or min(matrix[0, 0], matrix[1, 1]) <= 0 or not np.isfinite(matrix).all()
            or distortion.ndim != 1 or distortion.size not in (4, 5, 8, 12, 14)
            or not np.isfinite(distortion).all()):
        raise ValueError("la matriz o los coeficientes de lente no son válidos")
    scaled = np.diag((width / reference_width, height / reference_height, 1.0)) @ matrix
    return cv2.initUndistortRectifyMap(scaled, distortion, None, scaled, resolution, cv2.CV_16SC2)
