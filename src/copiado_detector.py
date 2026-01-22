import os
import time
from typing import Optional, Tuple

import cv2
import numpy as np

try:
    import pyautogui
except Exception as e:
    raise SystemExit(f"[ERROR] No se pudo importar pyautogui: {e}")


# Región base (asimétrica) + margen extra (+30 en todas direcciones)
_BASE_LEFT = 75
_BASE_RIGHT = 100
_BASE_UP = 10
_BASE_DOWN = 10

_EXTRA_MARGIN = 40  # <-- REQUERIDO: +30 en todas direcciones

LEFT = _BASE_LEFT + _EXTRA_MARGIN      # 105
RIGHT = _BASE_RIGHT + _EXTRA_MARGIN    # 130
UP = _BASE_UP + _EXTRA_MARGIN          # 50
DOWN = _BASE_DOWN + _EXTRA_MARGIN      # 50


# Escalas multiescala (incluye pequeñas para encajar en región)
SCALES = [
    0.30, 0.35, 0.40, 0.45, 0.50, 0.55, 0.60,
    0.70, 0.80, 0.90, 1.00, 1.10, 1.20
]


def _region_near_click(click_x: int, click_y: int) -> Tuple[int, int, int, int]:
    left = max(0, click_x - LEFT)
    top = max(0, click_y - UP)
    width = LEFT + RIGHT
    height = UP + DOWN
    return (left, top, width, height)


def _grab_region_bgr(region: Tuple[int, int, int, int]) -> np.ndarray:
    """
    region: (left, top, width, height)
    """
    img = pyautogui.screenshot(region=region)  # PIL
    bgr = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
    return bgr


def _save_debug_image(debug_dir: str, tag: str, bgr: np.ndarray):
    os.makedirs(debug_dir, exist_ok=True)
    ts = time.strftime("%Y%m%d_%H%M%S")
    path = os.path.join(debug_dir, f"{ts}_{tag}.png")
    cv2.imwrite(path, bgr)


def _match_multiscale(
    region_bgr: np.ndarray,
    template_path: str,
    thr: float,
) -> Tuple[bool, float, Optional[float]]:
    """
    Devuelve:
      (found, best_score, best_scale)
    """
    templ_bgr = cv2.imread(template_path, cv2.IMREAD_COLOR)
    if templ_bgr is None:
        raise FileNotFoundError(f"No se pudo leer template: {template_path}")

    region_g = cv2.cvtColor(region_bgr, cv2.COLOR_BGR2GRAY)
    templ_g0 = cv2.cvtColor(templ_bgr, cv2.COLOR_BGR2GRAY)

    rh, rw = region_g.shape[:2]

    best_score = -1.0
    best_scale = None

    for s in SCALES:
        th = int(templ_g0.shape[0] * s)
        tw = int(templ_g0.shape[1] * s)

        if th < 5 or tw < 5:
            continue
        if th > rh or tw > rw:
            continue

        templ_g = cv2.resize(templ_g0, (tw, th), interpolation=cv2.INTER_AREA)

        res = cv2.matchTemplate(region_g, templ_g, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, _ = cv2.minMaxLoc(res)

        if max_val > best_score:
            best_score = float(max_val)
            best_scale = float(s)

        if max_val >= thr:
            return True, float(max_val), float(s)

    return False, best_score, best_scale


def find_within_window_near_click(
    template_path: str,
    confidence: float,
    window_s: float,
    poll_s: float,
    click_x: int,
    click_y: int,
    debug: bool = False,
    debug_screenshots: bool = False,
    debug_dir: str = r".\debug_shots",
) -> bool:
    """
    Espera hasta window_s buscando template cerca del click.
    True si se detecta, False si timeout.
    """
    t0 = time.time()
    attempts = 0

    region = _region_near_click(click_x, click_y)

    if debug:
        print(f"  [DBG] region={region} thr={confidence} window_s={window_s} poll_s={poll_s} want_present=True")

    if debug_screenshots:
        bgr0 = _grab_region_bgr(region)
        _save_debug_image(debug_dir, "find_region_start", bgr0)

    while True:
        attempts += 1
        region_bgr = _grab_region_bgr(region)
        found, best_score, best_scale = _match_multiscale(region_bgr, template_path, confidence)

        if found:
            if debug:
                print(f"  [DBG] FOUND (score={best_score:.3f} scale={best_scale}) attempts={attempts}")
            return True

        if time.time() - t0 >= window_s:
            if debug:
                print(f"  [DBG] TIMEOUT waiting PRESENT after {time.time() - t0:.2f}s attempts={attempts} "
                      f"(best_score={best_score:.3f} best_scale={best_scale})")
            if debug_screenshots:
                _save_debug_image(debug_dir, "find_region_end_timeout", region_bgr)
            return False

        time.sleep(poll_s)


def wait_until_absent_near_click(
    template_path: str,
    confidence: float,
    window_s: float,
    poll_s: float,
    click_x: int,
    click_y: int,
    debug: bool = False,
    debug_screenshots: bool = False,
    debug_dir: str = r".\debug_shots",
) -> bool:
    """
    Espera hasta window_s a que el template NO esté presente cerca del click.
    True si desaparece, False si timeout.
    """
    t0 = time.time()
    attempts = 0

    region = _region_near_click(click_x, click_y)

    if debug:
        print(f"  [DBG] region={region} thr={confidence} window_s={window_s} poll_s={poll_s} want_present=False")

    if debug_screenshots:
        bgr0 = _grab_region_bgr(region)
        _save_debug_image(debug_dir, "absent_region_start", bgr0)

    while True:
        attempts += 1
        region_bgr = _grab_region_bgr(region)
        found, best_score, best_scale = _match_multiscale(region_bgr, template_path, confidence)

        if not found:
            if debug:
                print(f"  [DBG] ABSENT (best_seen_score={best_score:.3f} best_scale={best_scale}) attempts={attempts}")
            return True

        if time.time() - t0 >= window_s:
            if debug:
                print(f"  [DBG] TIMEOUT waiting ABSENT after {time.time() - t0:.2f}s attempts={attempts} "
                      f"(best_score={best_score:.3f} best_scale={best_scale})")
            if debug_screenshots:
                _save_debug_image(debug_dir, "absent_region_end_timeout", region_bgr)
            return False

        time.sleep(poll_s)
