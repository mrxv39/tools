import cv2
import numpy as np

from src.template_match import match_multiscale


def _make_template(w: int, h: int) -> np.ndarray:
    img = np.full((h, w), 255, dtype=np.uint8)
    # patrón con bordes (robusto para match)
    cv2.rectangle(img, (10, 10), (w - 10, h - 10), 0, 2)
    cv2.line(img, (10, h // 2), (w - 10, h // 2), 0, 2)
    cv2.putText(img, "X", (w // 3, int(h * 0.75)), cv2.FONT_HERSHEY_SIMPLEX, 1.2, 0, 2, cv2.LINE_AA)
    return img


def test_match_multiscale_detects_when_template_must_scale_down():
    template = _make_template(353, 100)  # similar a copiarcodigo.png
    # región chica tipo (175x40)
    haystack = np.full((40, 175), 255, dtype=np.uint8)

    # insertamos dentro de haystack una versión escalada del template
    scaled = cv2.resize(template, (175, 40), interpolation=cv2.INTER_AREA)
    haystack[:, :] = scaled

    assert match_multiscale(haystack, template, threshold=0.70) is True
