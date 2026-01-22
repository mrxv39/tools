
import time
import subprocess
import os

import win32gui
import win32con
import win32process


def _enum_windows():
    results = []

    def callback(hwnd, _):
        if not win32gui.IsWindowVisible(hwnd):
            return
        title = win32gui.GetWindowText(hwnd) or ""
        if not title.strip():
            return
        _, pid = win32process.GetWindowThreadProcessId(hwnd)
        results.append((hwnd, title, pid))

    win32gui.EnumWindows(callback, None)
    return results


def _activate_window(hwnd: int) -> bool:
    try:
        win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
        win32gui.SetForegroundWindow(hwnd)
        return True
    except Exception:
        return False


def activate_by_title_contains(title_contains: tuple) -> bool:
    windows = _enum_windows()
    for hwnd, title, _pid in reversed(windows):
        lt = title.lower()
        for s in title_contains:
            if s.lower() in lt:
                return _activate_window(hwnd)
    return False


def activate_or_launch(title_contains: tuple, launch_cmd: list) -> bool:
    if activate_by_title_contains(title_contains):
        return True

    if launch_cmd:
        try:
            subprocess.Popen(launch_cmd)
        except Exception:
            return False

        t0 = time.time()
        while time.time() - t0 < 3.0:
            if activate_by_title_contains(title_contains):
                return True
            time.sleep(0.1)

    return False


def _score_sublime_window(title: str, project_folder: str | None, file_path: str | None) -> int:
    """
    Puntúa una ventana de Sublime según si el título contiene:
    - nombre del proyecto (folder name)
    - nombre del archivo
    """
    lt = (title or "").lower()
    score = 0

    if "sublime text" not in lt:
        return -1

    if project_folder:
        folder_name = os.path.basename(project_folder.rstrip("\\/")).lower()
        if folder_name and folder_name in lt:
            score += 5

    if file_path:
        file_name = os.path.basename(file_path).lower()
        if file_name and file_name in lt:
            score += 7

    return score


def activate_sublime_for_project(project_folder: str | None, file_path: str | None) -> bool:
    """
    Si hay varios Sublime, intenta activar el que "parezca" tener el proyecto
    (por título). Elige el de mayor score.
    """
    windows = _enum_windows()
    best = None  # (score, hwnd)

    for hwnd, title, _pid in windows:
        sc = _score_sublime_window(title, project_folder, file_path)
        if sc >= 0:
            if best is None or sc > best[0]:
                best = (sc, hwnd)

    if best:
        return _activate_window(best[1])

    return False


def launch_sublime_opening_file(sublime_exe: str, project_folder: str | None, file_path: str | None) -> bool:
    """
    Lanza Sublime abriendo el archivo y añadiendo el folder del proyecto si existe.
    """
    if not sublime_exe:
        return False

    cmd = [sublime_exe]

    # Sublime soporta: sublime_text.exe --add <folder> <file>
    if project_folder:
        cmd += ["--add", project_folder]
    if file_path:
        cmd += [file_path]

    try:
        subprocess.Popen(cmd)
        return True
    except Exception:
        return False
