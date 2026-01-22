import time
import os
import subprocess

from src.classify import classify_target
from src.windowing import (
    activate_sublime_for_project,
    launch_sublime_opening_file,
)
from src.paste_actions import with_temporary_clipboard, paste_into_active_window
from src.fs_utils import ensure_file_exists


def _launch_new_cmd_and_paste(text: str, press_enter: bool):
    """
    Abre SIEMPRE una nueva ventana de CMD y pega el texto ahí.
    """
    subprocess.Popen(["cmd.exe"], creationflags=subprocess.CREATE_NEW_CONSOLE)
    time.sleep(0.6)
    with_temporary_clipboard(text, lambda: paste_into_active_window(press_enter))


def _launch_new_powershell_and_paste(text: str, press_enter: bool):
    """
    Abre SIEMPRE una nueva ventana de PowerShell y pega el texto ahí.
    """
    subprocess.Popen(
        ["powershell.exe"],
        creationflags=subprocess.CREATE_NEW_CONSOLE,
    )
    time.sleep(0.6)
    with_temporary_clipboard(text, lambda: paste_into_active_window(press_enter))


def route_payload(cfg, payload_text: str, file_path: str | None, project_folder: str | None):
    target = classify_target(payload_text)
    print(f"[{time.strftime('%H:%M:%S')}] Copiado detectado -> destino: {target}")

    # ===== CMD =====
    if target == "cmd":
        if cfg.debug:
            print("  [DBG] launching NEW CMD window")
        _launch_new_cmd_and_paste(payload_text, cfg.press_enter_in_terminal)
        return

    # ===== POWERSHELL =====
    if target == "powershell":
        if cfg.debug:
            print("  [DBG] launching NEW PowerShell window")
        _launch_new_powershell_and_paste(payload_text, cfg.press_enter_in_terminal)
        return

    # ===== SUBLIME =====
    if not file_path:
        print("  [WARN] Bloqueado: destino=sublime pero el portapapeles NO trae ruta de archivo en la primera línea.")
        print("  [WARN] Formato requerido:\n"
              "         C:\\ruta\\al\\archivo.ext\n"
              "         <código...>\n")
        return

    file_path = os.path.normpath(file_path)

    try:
        created = ensure_file_exists(file_path)
    except Exception as e:
        print(f"  [ERROR] No se pudo asegurar/crear el archivo: {file_path} -> {e}")
        return

    if cfg.debug:
        print(f"  [DBG] sublime file_path={file_path}")
        print(f"  [DBG] sublime file_exists={os.path.exists(file_path)} created={created}")
        print(f"  [DBG] sublime project_folder={project_folder}")

    activated = activate_sublime_for_project(project_folder, file_path)
    if not activated:
        sublime_exe = cfg.sublime_launch[0] if cfg.sublime_launch else ""
        launch_sublime_opening_file(sublime_exe, project_folder, file_path)
        time.sleep(0.4)
        activate_sublime_for_project(project_folder, file_path)

    if payload_text.strip():
        with_temporary_clipboard(payload_text, lambda: paste_into_active_window(False))
