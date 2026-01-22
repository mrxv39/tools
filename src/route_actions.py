# C:\Users\Usuario\tools\chatgpt_router\src\route_actions.py
import time

from src.classify import classify_target
from src.windowing import (
    activate_or_launch,
    activate_sublime_for_project,
    launch_sublime_opening_file,
)
from src.paste_actions import with_temporary_clipboard, paste_into_active_window


def route_payload(cfg, payload_text: str, file_path: str | None, project_folder: str | None):
    target = classify_target(payload_text)
    print(f"[{time.strftime('%H:%M:%S')}] Copiado detectado -> destino: {target}")

    if target == "powershell":
        ok = activate_or_launch(cfg.powershell_title_contains, cfg.powershell_launch)
        if cfg.debug:
            print(f"  [DBG] activate powershell ok={ok}")
        if ok:
            with_temporary_clipboard(payload_text, lambda: paste_into_active_window(cfg.press_enter_in_terminal))
        return

    if target == "cmd":
        ok = activate_or_launch(cfg.cmd_title_contains, cfg.cmd_launch)
        if cfg.debug:
            print(f"  [DBG] activate cmd ok={ok}")
        if ok:
            with_temporary_clipboard(payload_text, lambda: paste_into_active_window(cfg.press_enter_in_terminal))
        return

    activated = activate_sublime_for_project(project_folder, file_path)
    if cfg.debug:
        print(f"  [DBG] activate_sublime_for_project(folder={project_folder}, file={file_path}) -> {activated}")

    if not activated:
        sublime_exe = cfg.sublime_launch[0] if cfg.sublime_launch else ""
        launched = launch_sublime_opening_file(sublime_exe, project_folder, file_path)
        if cfg.debug:
            print(f"  [DBG] launch_sublime_opening_file -> {launched}")
        time.sleep(0.4)
        activate_sublime_for_project(project_folder, file_path)

    if payload_text.strip():
        with_temporary_clipboard(payload_text, lambda: paste_into_active_window(False))
    else:
        if cfg.debug:
            print("  [DBG] payload_text vacío (nada que pegar)")
