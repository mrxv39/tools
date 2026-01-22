
import time
import os
import subprocess
import ctypes

from src.classify import classify_target
from src.windowing import (
    activate_sublime_for_project,
    launch_sublime_opening_file,
)
from src.paste_actions import (
    with_temporary_clipboard,
    paste_into_active_window,
    copy_all_text_from_active_window_to_clipboard,
)
from src.fs_utils import ensure_file_exists


def show_alert(title: str, message: str):
    """
    Popup simple en Windows (sin dependencias externas).
    """
    try:
        MB_OK = 0x0
        MB_ICONWARNING = 0x30
        ctypes.windll.user32.MessageBoxW(None, message, title, MB_OK | MB_ICONWARNING)
    except Exception:
        print(f"[ALERT] {title}: {message}")


def _launch_new_cmd_and_paste(text: str, press_enter: bool, copy_all_after: bool):
    subprocess.Popen(["cmd.exe"], creationflags=subprocess.CREATE_NEW_CONSOLE)
    time.sleep(0.6)
    with_temporary_clipboard(text, lambda: paste_into_active_window(press_enter))
    if copy_all_after:
        time.sleep(0.15)
        copy_all_text_from_active_window_to_clipboard()


def _launch_new_powershell_and_paste(text: str, press_enter: bool, copy_all_after: bool):
    subprocess.Popen(["powershell.exe"], creationflags=subprocess.CREATE_NEW_CONSOLE)
    time.sleep(0.6)
    with_temporary_clipboard(text, lambda: paste_into_active_window(press_enter))
    if copy_all_after:
        time.sleep(0.15)
        copy_all_text_from_active_window_to_clipboard()


def route_payload(cfg, payload_text: str, file_path: str | None, project_folder: str | None):
    target = classify_target(payload_text)
    print(f"[{time.strftime('%H:%M:%S')}] Copiado detectado -> destino: {target}")

    copy_all_after = bool(getattr(cfg, "copy_terminal_text_to_clipboard", True))
    press_enter = bool(getattr(cfg, "press_enter_in_terminal", False))

    # ===== CMD =====
    if target == "cmd":
        if getattr(cfg, "debug", False):
            print("  [DBG] launching NEW CMD window")
        _launch_new_cmd_and_paste(payload_text, press_enter, copy_all_after)
        return

    # ===== POWERSHELL =====
    if target == "powershell":
        if getattr(cfg, "debug", False):
            print("  [DBG] launching NEW PowerShell window")
        _launch_new_powershell_and_paste(payload_text, press_enter, copy_all_after)
        return

    # ===== SUBLIME =====
    if not file_path:
        msg = (
            "El contenido se clasificó para Sublime, pero NO trae ruta de archivo en la primera línea.\n\n"
            "Formato requerido:\n"
            "  C:\\ruta\\al\\archivo.ext\n"
            "  <código...>\n"
        )
        show_alert("chatgpt_router: falta ruta para Sublime", msg)
        return

    file_path = os.path.normpath(file_path)

    try:
        ensure_file_exists(file_path)
    except Exception as e:
        show_alert("chatgpt_router: no se pudo crear archivo", f"{file_path}\n\n{e}")
        return

    sublime_exe = cfg.sublime_launch[0] if getattr(cfg, "sublime_launch", None) else ""
    try:
        launch_sublime_opening_file(sublime_exe, project_folder, file_path)
    except Exception:
        pass

    time.sleep(0.4)
    activate_sublime_for_project(project_folder, file_path)
    time.sleep(0.25)

    if payload_text.strip():
        with_temporary_clipboard(payload_text, lambda: paste_into_active_window(False))
