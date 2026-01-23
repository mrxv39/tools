import time
import pyperclip


pyautogui = None
_pyautogui_import_error: Exception | None = None
try:
    import pyautogui as _pyautogui  # type: ignore
    pyautogui = _pyautogui
except Exception as e:
    # Allow importing in headless environments (e.g. CI) and fail only if
    # these UI actions are actually invoked.
    _pyautogui_import_error = e


def _require_pyautogui():
    if pyautogui is None:
        raise RuntimeError(f"pyautogui unavailable: {_pyautogui_import_error}")


def paste_into_active_window(press_enter: bool):
    _require_pyautogui()
    pyautogui.hotkey("ctrl", "v")
    time.sleep(0.05)
    if press_enter:
        pyautogui.press("enter")


def copy_all_text_from_active_window_to_clipboard():
    """
    CMD clásico: Ctrl+A a veces selecciona solo la línea actual en el primer intento.
    Hacemos Ctrl+A dos veces para forzar 'Select All' del buffer visible, y luego Ctrl+C.
    """
    _require_pyautogui()
    pyautogui.hotkey("ctrl", "a")
    time.sleep(0.05)
    pyautogui.hotkey("ctrl", "a")
    time.sleep(0.05)
    pyautogui.hotkey("ctrl", "c")
    time.sleep(0.08)


def with_temporary_clipboard(text_to_paste: str, fn):
    try:
        original = pyperclip.paste()
    except Exception:
        original = ""

    try:
        pyperclip.copy(text_to_paste)
        time.sleep(0.03)
        fn()
    finally:
        try:
            pyperclip.copy(original)
        except Exception:
            pass
