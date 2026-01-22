# C:\Users\Usuario\tools\chatgpt_router\src\copiado_detector.py
import os
import time
from typing import Tuple

import cv2
import numpy as np
import mss
import pyautogui


def _clamp_region(left: int, top: int, width: int, height: int) -> Tuple[int, int, int, int]:
    sw, sh = pyautogui.size()

    left = max(0, left)
    top = max(0, top)

    width = min(width, sw - left)
    height = min(height, sh - top)

    width = max(1, width)
    height = max(1, height)

    return (left, top, width, height)


def _save_region_shot_mss(debug_dir: str, region: Tuple[int, int, int, int], tag: str):
    os.makedirs(debug_dir, exist_ok=True)
    ts = time.strftime("%Y%m%d_%H%M%S")
    path = os.path.join(debug_dir, f"{ts}_{tag}.png")

    left, top, width, height = region
    mon = {"left": left, "top": top, "width": width, "height": height}

    try:
        with mss.mss() as sct:
            img = np.array(sct.grab(mon))  # BGRA
        bgr = img[:, :, :3]
        cv2.imwrite(path, bgr)
        return path
    except Exception:
        return None


def _load_template_gray(template_path: str) -> np.ndarray:
    tmpl = cv2.imread(template_path, cv2.IMREAD_GRAYSCALE)
    if tmpl is None:
        raise FileNotFoundError(f"No se pudo leer template: {template_path}")
    return tmpl


def _match_multiscale(haystack_gray: np.ndarray, template_gray: np.ndarray, threshold: float) -> bool:
    """
    Multi-escala (pocas escalas para que sea rápido).
    """
    hH, hW = haystack_gray.shape[:2]
    tH0, tW0 = template_gray.shape[:2]

    scales = [0.90, 1.00, 1.10, 1.20]  # suficiente en la práctica

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


def find_within_window_near_click(
    template_path: str,
    confidence: float,
    window_s: float,
    poll_s: float,
    click_x: int,
    click_y: int,
    half_box_px: int = 50,   # ✅ 50 px por lado
    debug: bool = False,
    debug_screenshots: bool = False,
    debug_dir: str = r".\debug_shots",
) -> bool:
    """
    Busca el template SOLO en un área (2*half_box_px)x(2*half_box_px)
    centrada en el click (50px izq/der/arr/abajo por defecto).
    """
    size = int(half_box_px) * 2
    left = int(click_x - half_box_px)
    top = int(click_y - half_box_px)
    region = _clamp_region(left, top, size, size)

    if debug:
        print(f"  [DBG] region={region} thr={confidence} window_s={window_s} poll_s={poll_s}")

    if debug and debug_screenshots:
        p = _save_region_shot_mss(debug_dir, region, "region_start")
        if p:
            print(f"  [DBG] saved region_start: {p}")

    template_gray = _load_template_gray(template_path)

    attempts = 0
    t0 = time.time()

    r_left, r_top, r_w, r_h = region
    mon = {"left": r_left, "top": r_top, "width": r_w, "height": r_h}

    with mss.mss() as sct:
        while time.time() - t0 < window_s:
            attempts += 1
            try:
                img = np.array(sct.grab(mon))   # BGRA
                gray = cv2.cvtColor(img[:, :, :3], cv2.COLOR_BGR2GRAY)

                if _match_multiscale(gray, template_gray, confidence):
                    if debug:
                        dt = time.time() - t0
                        print(f"  [DBG] FOUND (mss+cv2) in {dt:.2f}s attempts={attempts}")
                    return True
            except Exception as e:
                if debug:
                    print(f"  [DBG] match error: {type(e).__name__}: {e}")

            time.sleep(poll_s)

    if debug:
        dt = time.time() - t0
        print(f"  [DBG] NOT FOUND after {dt:.2f}s attempts={attempts}")

    if debug and debug_screenshots:
        p = _save_region_shot_mss(debug_dir, region, "region_end_notfound")
        if p:
            print(f"  [DBG] saved region_end_notfound: {p}")

    return False
