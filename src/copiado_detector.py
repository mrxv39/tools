import time
from typing import Tuple

import mss

from src.screen_capture import clamp_region, save_region_shot_mss, region_to_mon, grab_gray
from src.template_match import load_template_gray, match_multiscale


def _region_from_click(click_x: int, click_y: int, half_box_px: int) -> Tuple[int, int, int, int]:
    size = int(half_box_px) * 2
    left = int(click_x - half_box_px)
    top = int(click_y - half_box_px)
    return clamp_region(left, top, size, size)


def _poll_template_in_region(
    template_path: str,
    confidence: float,
    window_s: float,
    poll_s: float,
    region: Tuple[int, int, int, int],
    want_present: bool,
    debug: bool,
    debug_screenshots: bool,
    debug_dir: str,
    tag_prefix: str,
) -> bool:
    if debug:
        print(f"  [DBG] region={region} thr={confidence} window_s={window_s} poll_s={poll_s} want_present={want_present}")

    if debug and debug_screenshots:
        p = save_region_shot_mss(debug_dir, region, f"{tag_prefix}_region_start")
        if p:
            print(f"  [DBG] saved {tag_prefix}_region_start: {p}")

    template_gray = load_template_gray(template_path)

    attempts = 0
    t0 = time.time()
    mon = region_to_mon(region)

    with mss.mss() as sct:
        while time.time() - t0 < window_s:
            attempts += 1
            try:
                gray = grab_gray(sct, mon)
                is_present = match_multiscale(gray, template_gray, confidence)
                if is_present == want_present:
                    if debug:
                        dt = time.time() - t0
                        state = "PRESENT" if want_present else "ABSENT"
                        print(f"  [DBG] OK ({state}) in {dt:.2f}s attempts={attempts}")
                    return True
            except Exception as e:
                if debug:
                    print(f"  [DBG] match error: {type(e).__name__}: {e}")

            time.sleep(poll_s)

    if debug:
        dt = time.time() - t0
        state = "PRESENT" if want_present else "ABSENT"
        print(f"  [DBG] TIMEOUT waiting {state} after {dt:.2f}s attempts={attempts}")

    if debug and debug_screenshots:
        p = save_region_shot_mss(debug_dir, region, f"{tag_prefix}_region_end_timeout")
        if p:
            print(f"  [DBG] saved {tag_prefix}_region_end_timeout: {p}")

    return False


def find_within_window_near_click(
    template_path: str,
    confidence: float,
    window_s: float,
    poll_s: float,
    click_x: int,
    click_y: int,
    half_box_px: int = 50,
    debug: bool = False,
    debug_screenshots: bool = False,
    debug_dir: str = r".\debug_shots",
) -> bool:
    region = _region_from_click(click_x, click_y, half_box_px)
    return _poll_template_in_region(
        template_path=template_path,
        confidence=confidence,
        window_s=window_s,
        poll_s=poll_s,
        region=region,
        want_present=True,
        debug=debug,
        debug_screenshots=debug_screenshots,
        debug_dir=debug_dir,
        tag_prefix="find",
    )


def wait_until_absent_near_click(
    template_path: str,
    confidence: float,
    window_s: float,
    poll_s: float,
    click_x: int,
    click_y: int,
    half_box_px: int = 50,
    debug: bool = False,
    debug_screenshots: bool = False,
    debug_dir: str = r".\debug_shots",
) -> bool:
    region = _region_from_click(click_x, click_y, half_box_px)
    return _poll_template_in_region(
        template_path=template_path,
        confidence=confidence,
        window_s=window_s,
        poll_s=poll_s,
        region=region,
        want_present=False,
        debug=debug,
        debug_screenshots=debug_screenshots,
        debug_dir=debug_dir,
        tag_prefix="wait_absent",
    )
