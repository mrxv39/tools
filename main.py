# C:\Users\Usuario\tools\chatgpt_router\main.py
import time

import pyautogui

from src.config import load_config
from src.runtime import RouterRuntime


def main():
    cfg = load_config()
    pyautogui.FAILSAFE = True

    print("ChatGPT Copiado Router (MSS + región ±50px + main segmentado)")
    print("- Solo actúa si la ventana activa es un navegador")
    print("- Click izquierdo → encola (no bloquea ratón)")
    print("- Worker → busca 'Copiado' SOLO ±half_box_px desde el click")
    print("- Ctrl+Shift+Q o Ctrl+C → salir\n")

    if cfg.debug:
        print(f"[DBG] template={cfg.template_copiado_path}")
        print(f"[DBG] thr={cfg.image_confidence} half_box_px={cfg.half_box_px} window={cfg.search_window_s}s poll={cfg.search_poll_interval_s}s\n")

    runtime = RouterRuntime(cfg)
    runtime.start()

    try:
        while runtime.is_running():
            time.sleep(0.2)
    except KeyboardInterrupt:
        print("\n[Router detenido por Ctrl+C]")
    finally:
        runtime.stop()


if __name__ == "__main__":
    main()
