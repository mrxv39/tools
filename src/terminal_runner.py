from __future__ import annotations

import subprocess
import time

from src.paste_actions import (
    with_temporary_clipboard,
    paste_into_active_window,
    copy_all_text_from_active_window_to_clipboard,
)
from src.terminal_sync import build_payload_with_sentinel, copy_terminal_output_until_done


def run_in_new_cmd(cfg, user_text: str) -> None:
    press_enter = bool(getattr(cfg, "press_enter_in_terminal", False))
    copy_all_after = bool(getattr(cfg, "copy_terminal_text_to_clipboard", True))

    subprocess.Popen(["cmd.exe"], creationflags=subprocess.CREATE_NEW_CONSOLE)
    time.sleep(0.6)

    text_to_paste = user_text
    if press_enter and copy_all_after:
        text_to_paste = build_payload_with_sentinel("cmd", user_text)

    with_temporary_clipboard(text_to_paste, lambda: paste_into_active_window(press_enter))

    if copy_all_after:
        if press_enter:
            timeout_s = float(getattr(cfg, "terminal_done_timeout_s", 10.0))
            poll_s = float(getattr(cfg, "terminal_done_poll_s", 0.20))
            copy_terminal_output_until_done(
                copy_all_text_from_active_window_to_clipboard,
                timeout_s,
                poll_s,
            )
        else:
            copy_all_text_from_active_window_to_clipboard()


def run_in_new_powershell(cfg, user_text: str) -> None:
    press_enter = bool(getattr(cfg, "press_enter_in_terminal", False))
    copy_all_after = bool(getattr(cfg, "copy_terminal_text_to_clipboard", True))

    subprocess.Popen(["powershell.exe"], creationflags=subprocess.CREATE_NEW_CONSOLE)
    time.sleep(0.6)

    text_to_paste = user_text
    if press_enter and copy_all_after:
        text_to_paste = build_payload_with_sentinel("powershell", user_text)

    with_temporary_clipboard(text_to_paste, lambda: paste_into_active_window(press_enter))

    if copy_all_after:
        if press_enter:
            timeout_s = float(getattr(cfg, "terminal_done_timeout_s", 10.0))
            poll_s = float(getattr(cfg, "terminal_done_poll_s", 0.20))
            copy_terminal_output_until_done(
                copy_all_text_from_active_window_to_clipboard,
                timeout_s,
                poll_s,
            )
        else:
            copy_all_text_from_active_window_to_clipboard()
