# C:\Users\Usuario\tools\chatgpt_router\src\runtime.py
import queue
import threading
import time

from pynput import mouse, keyboard

from src.active_window import is_active_window_browser
from src.copiado_detector import find_within_window_near_click
from src.clipboard_parse import parse_clipboard
from src.route_actions import route_payload
from src.clipboard_io import safe_paste_clipboard


class RouterRuntime:
    def __init__(self, cfg):
        self.cfg = cfg
        self._running = False

        self._q = queue.Queue(maxsize=5)
        self._worker_thread = None

        self._mouse_listener = None
        self._keyboard_listener = None

        self._last_action_ts = 0.0
        self._last_seen_clip = ""

        self._pressed_keys = set()

    def is_running(self) -> bool:
        return self._running

    def start(self):
        if self._running:
            return
        self._running = True

        # worker
        self._worker_thread = threading.Thread(target=self._worker_loop, daemon=True)
        self._worker_thread.start()

        # listeners
        self._mouse_listener = mouse.Listener(on_click=self._on_click)
        self._keyboard_listener = keyboard.Listener(on_press=self._on_press, on_release=self._on_release)

        self._mouse_listener.start()
        self._keyboard_listener.start()

    def stop(self):
        if not self._running:
            return
        self._running = False

        try:
            if self._mouse_listener:
                self._mouse_listener.stop()
        except Exception:
            pass

        try:
            if self._keyboard_listener:
                self._keyboard_listener.stop()
        except Exception:
            pass

    # --------------------
    # Mouse: NO hace trabajo pesado. Solo encola.
    # --------------------
    def _on_click(self, x, y, button, pressed):
        if not self._running:
            return False
        if button != mouse.Button.left or pressed:
            return

        try:
            self._q.put_nowait((int(x), int(y), time.time()))
        except queue.Full:
            if self.cfg.debug:
                print("  [DBG] queue full: drop click")

    # --------------------
    # Keyboard: Ctrl+Shift+Q para salir
    # --------------------
    def _on_press(self, key):
        if not self._running:
            return False

        self._pressed_keys.add(key)

        ctrl = (keyboard.Key.ctrl_l in self._pressed_keys) or (keyboard.Key.ctrl_r in self._pressed_keys)
        shift = (
            (keyboard.Key.shift in self._pressed_keys)
            or (keyboard.Key.shift_l in self._pressed_keys)
            or (keyboard.Key.shift_r in self._pressed_keys)
        )

        if ctrl and shift:
            try:
                if key.char.lower() == "q":
                    print("\n[Router detenido por Ctrl+Shift+Q]")
                    self.stop()
                    return False
            except Exception:
                pass

    def _on_release(self, key):
        try:
            self._pressed_keys.discard(key)
        except Exception:
            pass

    # --------------------
    # Worker: aquí va el trabajo pesado
    # --------------------
    def _worker_loop(self):
        while self._running:
            try:
                x, y, ts = self._q.get(timeout=0.2)
            except queue.Empty:
                continue

            try:
                self._process_click(x, y, ts)
            finally:
                try:
                    self._q.task_done()
                except Exception:
                    pass

    def _process_click(self, x: int, y: int, ts: float):
        # cooldown
        if ts - self._last_action_ts < self.cfg.cooldown_s:
            if self.cfg.debug:
                print("  [DBG] worker: ignored (cooldown)")
            return

        # solo si ventana activa es navegador
        if not is_active_window_browser():
            if self.cfg.debug:
                print("  [DBG] worker: ignored (active window NOT browser)")
            return

        if self.cfg.debug:
            print(f"[{time.strftime('%H:%M:%S')}] click queued x={x} y={y} (browser ok)")

        found = find_within_window_near_click(
            template_path=self.cfg.template_copiado_path,
            confidence=self.cfg.image_confidence,
            window_s=self.cfg.search_window_s,
            poll_s=self.cfg.search_poll_interval_s,
            click_x=int(x),
            click_y=int(y),
            half_box_px=self.cfg.half_box_px,
            debug=self.cfg.debug,
            debug_screenshots=self.cfg.debug_screenshots,
            debug_dir=self.cfg.debug_dir,
        )

        if not found:
            if self.cfg.debug:
                print("  [DBG] worker: image NOT found")
            return

        clip = safe_paste_clipboard(self.cfg)
        if not clip.strip():
            if self.cfg.debug:
                print("  [DBG] worker: clipboard empty")
            return

        if clip == self._last_seen_clip:
            if self.cfg.debug:
                print("  [DBG] worker: clipboard unchanged (ignored)")
            self._last_action_ts = ts
            return

        self._last_seen_clip = clip
        self._last_action_ts = ts

        parsed = parse_clipboard(clip)
        payload_text = parsed.content if parsed.file_path else clip

        if self.cfg.debug and parsed.file_path:
            print(f"  [DBG] parsed file_path={parsed.file_path}")
            print(f"  [DBG] parsed project_folder={parsed.project_folder}")

        route_payload(self.cfg, payload_text, parsed.file_path, parsed.project_folder)
