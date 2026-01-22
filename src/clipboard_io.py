
import pyperclip


def safe_paste_clipboard(cfg) -> str:
    try:
        return pyperclip.paste() or ""
    except Exception as e:
        if getattr(cfg, "debug", False):
            print(f"  [DBG] worker: clipboard read error: {e}")
        return ""
