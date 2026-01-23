import os
import time
import ctypes

from src.classify import classify_target
from src.file_writer import write_text_file
from src.terminal_runner import run_in_new_cmd, run_in_new_powershell


def show_alert(title: str, message: str):
    try:
        MB_OK = 0x0
        MB_ICONWARNING = 0x30
        ctypes.windll.user32.MessageBoxW(None, message, title, MB_OK | MB_ICONWARNING)
    except Exception:
        print(f"[ALERT] {title}: {message}")


def route_payload(cfg, payload_text: str, file_path: str | None, project_folder: str | None):
    target = classify_target(payload_text)
    print(f"[{time.strftime('%H:%M:%S')}] Copiado detectado -> destino: {target}")

    if target == "cmd":
        run_in_new_cmd(cfg, payload_text)
        return

    if target == "powershell":
        run_in_new_powershell(cfg, payload_text)
        return

    # Caso: NO es cmd ni powershell => debe venir ruta en primera línea del portapapeles (ya parseada)
    if not file_path:
        show_alert(
            "Archivo bloqueado",
            "El portapapeles NO trae ruta de archivo en la primera línea",
        )
        return

    file_path = os.path.normpath(file_path)

    try:
        write_text_file(file_path, payload_text or "")
    except Exception as e:
        show_alert("No se pudo escribir archivo", f"{file_path}\n\n{e}")
        return
