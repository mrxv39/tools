import os
import time
from typing import Tuple, Optional

import cv2
import mss
import numpy as np
import pyautogui


def clamp_region(left: int, top: int, width: int, height: int) -> Tuple[int, int, int, int]:
    sw, sh = pyautogui.size()

    left = max(0, left)
    top = max(0, top)

    width = min(width, sw - left)
    height = min(height, sh - top)

    width = max(1, width)
    height = max(1, height)

    return (left, top, width, height)


def save_region_shot_mss(debug_dir: str, region: Tuple[int, int, int, int], tag: str) -> Optional[str]:
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


def region_to_mon(region: Tuple[int, int, int, int]) -> dict:
    left, top, width, height = region
    return {"left": left, "top": top, "width": width, "height": height}


def grab_gray(sct: mss.mss, mon: dict) -> np.ndarray:
    img = np.array(sct.grab(mon))  # BGRA
    return cv2.cvtColor(img[:, :, :3], cv2.COLOR_BGR2GRAY)
