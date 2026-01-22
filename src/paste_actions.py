# C:\Users\Usuario\tools\chatgpt_router\src\paste_actions.py
import time
import pyautogui
import pyperclip


def paste_into_active_window(press_enter: bool):
    pyautogui.hotkey("ctrl", "v")
    time.sleep(0.05)
    if press_enter:
        pyautogui.press("enter")


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
