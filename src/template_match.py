import cv2
import numpy as np


def load_template_gray(template_path: str) -> np.ndarray:
    tmpl = cv2.imread(template_path, cv2.IMREAD_GRAYSCALE)
    if tmpl is None:
        raise FileNotFoundError(f"No se pudo leer template: {template_path}")
    return tmpl


def match_multiscale(haystack_gray: np.ndarray, template_gray: np.ndarray, threshold: float) -> bool:
    hH, hW = haystack_gray.shape[:2]
    tH0, tW0 = template_gray.shape[:2]

    # IMPORTANTE:
    # tus regiones ahora son ~175x40, pero los templates son más grandes (p.ej. 353x100).
    # necesitamos escalas pequeñas (~0.40-0.55) para que quepan.
    scales = [
        0.30, 0.35, 0.40, 0.45, 0.50, 0.55, 0.60, 0.70, 0.80, 0.90,
        1.00, 1.10, 1.20,
    ]

    for s in scales:
        tW = int(tW0 * s)
        tH = int(tH0 * s)

        if tW < 6 or tH < 6:
            continue
        if tW > hW or tH > hH:
            continue

        tmpl_rs = cv2.resize(template_gray, (tW, tH), interpolation=cv2.INTER_AREA)
        res = cv2.matchTemplate(haystack_gray, tmpl_rs, cv2.TM_CCOEFF_NORMED)
        _minVal, maxVal, _minLoc, _maxLoc = cv2.minMaxLoc(res)

        if maxVal >= threshold:
            return True

    return False
