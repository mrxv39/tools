import time
from typing import Callable, Optional

from pynput import mouse, keyboard


class InputListeners:
    def __init__(
        self,
        running_fn: Callable[[], bool],
        enqueue_click_fn: Callable[[int, int, float], None],
        on_stop_fn: Callable[[], None],
        debug: bool = False,
    ):
        self._running_fn = running_fn
        self._enqueue_click_fn = enqueue_click_fn
        self._on_stop_fn = on_stop_fn
        self._debug = debug

        self._mouse_listener: Optional[mouse.Listener] = None
        self._keyboard_listener: Optional[keyboard.Listener] = None
        self._pressed_keys = set()

    def start(self):
        self._mouse_listener = mouse.Listener(on_click=self._on_click)
        self._keyboard_listener = keyboard.Listener(on_press=self._on_press, on_release=self._on_release)
        self._mouse_listener.start()
        self._keyboard_listener.start()

    def stop(self):
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

    def _on_click(self, x, y, button, pressed):
        if not self._running_fn():
            return False
        if button != mouse.Button.left or pressed:
            return

        try:
            self._enqueue_click_fn(int(x), int(y), time.time())
        except Exception:
            if self._debug:
                print("  [DBG] enqueue click failed")

    def _on_press(self, key):
        if not self._running_fn():
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
                    self._on_stop_fn()
                    return False
            except Exception:
                pass

    def _on_release(self, key):
        try:
            self._pressed_keys.discard(key)
        except Exception:
            pass
