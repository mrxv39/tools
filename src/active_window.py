# C:\Users\Usuario\tools\chatgpt_router\src\active_window.py
import win32gui
import win32process
import psutil


# Ejecutables típicos de navegadores
BROWSER_EXES = {
    "chrome.exe",
    "msedge.exe",
    "firefox.exe",
    "brave.exe",
    "opera.exe",
    "vivaldi.exe",
}


def _get_foreground_hwnd():
    return win32gui.GetForegroundWindow()


def _get_process_exe_name(hwnd: int) -> str:
    try:
        _, pid = win32process.GetWindowThreadProcessId(hwnd)
        p = psutil.Process(pid)
        return (p.name() or "").lower()
    except Exception:
        return ""


def is_active_window_browser() -> bool:
    """
    Devuelve True si la ventana activa pertenece a un navegador web.
    """
    hwnd = _get_foreground_hwnd()
    if not hwnd:
        return False

    exe = _get_process_exe_name(hwnd)
    return exe in BROWSER_EXES
