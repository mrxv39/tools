# C:\Users\Usuario\tools\chatgpt_router\router_copiado.py
import time
import re
import subprocess
from dataclasses import dataclass

import pyautogui
import pyperclip

import win32gui
import win32con
import win32process


# =========================
# CONFIG
# =========================

@dataclass
class Config:
    # Imagen del "✓ Copiado" (template)
    template_copiado_path: str = r".\copiado.png"

    # Cada cuánto buscar la imagen en pantalla (segundos)
    poll_interval_s: float = 0.25

    # Confianza para match (requiere opencv-python). Ajusta entre 0.70 y 0.95.
    image_confidence: float = 0.85

    # Debounce: una vez detectado, no volver a actuar durante X segundos
    cooldown_s: float = 1.2

    # Si True: además de pegar, pulsa Enter en terminal (CMD/PS).
    press_enter_in_terminal: bool = False

    # Títulos (o partes) típicos de ventanas a activar (contains)
    cmd_title_contains: tuple = ("Command Prompt", "cmd.exe", "Símbolo del sistema")
    powershell_title_contains: tuple = ("Windows PowerShell", "PowerShell", "pwsh", "Terminal")
    sublime_title_contains: tuple = ("Sublime Text",)

    # Cómo lanzar si no existe
    cmd_launch: list = None
    powershell_launch: list = None
    sublime_launch: list = None


CFG = Config(
    template_copiado_path=r".\copiado.png",
    poll_interval_s=0.25,
    image_confidence=0.85,
    cooldown_s=1.2,
    press_enter_in_terminal=False,
    cmd_launch=["cmd.exe"],
    powershell_launch=["powershell.exe"],  # o ["pwsh.exe"] si usas PowerShell 7
    sublime_launch=[r"C:\Program Files\Sublime Text\sublime_text.exe"],  # ajusta si difiere
)


# =========================
# WINDOW HELPERS (Win32)
# =========================

def _enum_windows():
    """Devuelve una lista de (hwnd, title, pid)."""
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
    """Activa la primera ventana cuyo título contenga alguno de los substrings."""
    windows = _enum_windows()
    for hwnd, title, _pid in reversed(windows):
        lt = title.lower()
        for s in title_contains:
            if s.lower() in lt:
                return _activate_window(hwnd)
    return False


def activate_or_launch(title_contains: tuple, launch_cmd: list) -> bool:
    """Activa si existe; si no, lanza y reintenta."""
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


# =========================
# CLASSIFICATION (CMD / PS / SUBLIME)
# =========================

def looks_like_powershell(text: str) -> bool:
    t = text.strip()

    ps_cmdlets = [
        r"\bGet-\w+\b", r"\bSet-\w+\b", r"\bNew-\w+\b", r"\bRemove-\w+\b",
        r"\bStart-\w+\b", r"\bStop-\w+\b", r"\bSelect-Object\b", r"\bWhere-Object\b",
        r"\bForEach-Object\b", r"\bOut-File\b", r"\bFormat-Table\b",
    ]
    if any(re.search(p, t) for p in ps_cmdlets):
        return True

    if re.search(r"\$env:\w+", t):
        return True
    if re.search(r"\$\w+", t) and ("=" in t or "|" in t):
        return True
    if re.search(r"\b-Path\b|\b-Recurse\b|\b-Force\b|\b-ErrorAction\b", t):
        return True

    if "|" in t and re.search(r"\b(Select|Where|ForEach|Out|Format)\b", t, re.IGNORECASE):
        return True

    return False


def looks_like_cmd(text: str) -> bool:
    t = text.strip()

    cmd_starts = [
        r"^\s*(cd|dir|cls|echo|set|type|copy|move|del|erase|rd|rmdir|mkdir|ren|rename)\b",
        r"^\s*(git|pip|python|py|node|npm|npx|yarn|pnpm|docker|kubectl|flyctl)\b",
    ]
    if any(re.search(p, t, re.IGNORECASE) for p in cmd_starts):
        return True

    if re.search(r"(&&|\|\|)\s*\S+", t):
        return True

    if re.search(r"^[A-Za-z]:\\", t) and " " in t:
        return True

    return False


def classify_target(text: str) -> str:
    """Devuelve: 'powershell' | 'cmd' | 'sublime'."""
    if looks_like_powershell(text):
        return "powershell"
    if looks_like_cmd(text):
        return "cmd"
    return "sublime"


# =========================
# MAIN LOOP
# =========================

def wait_for_copiado_image(template_path: str, confidence: float) -> bool:
    """
    True si se encuentra el template en pantalla.
    Requiere opencv-python para confidence.
    """
    try:
        region = pyautogui.locateOnScreen(template_path, confidence=confidence)
        return region is not None
    except Exception:
        # fallback si no hay OpenCV o falla
        try:
            region = pyautogui.locateOnScreen(template_path)
            return region is not None
        except Exception:
            return False


def paste_into_active_window(press_enter: bool):
    pyautogui.hotkey("ctrl", "v")
    time.sleep(0.05)
    if press_enter:
        pyautogui.press("enter")


def handle_clipboard_routing(text: str):
    target = classify_target(text)

    if target == "powershell":
        ok = activate_or_launch(CFG.powershell_title_contains, CFG.powershell_launch)
        if ok:
            paste_into_active_window(CFG.press_enter_in_terminal)

    elif target == "cmd":
        ok = activate_or_launch(CFG.cmd_title_contains, CFG.cmd_launch)
        if ok:
            paste_into_active_window(CFG.press_enter_in_terminal)

    else:
        ok = activate_or_launch(CFG.sublime_title_contains, CFG.sublime_launch)
        if ok:
            paste_into_active_window(False)


def main():
    print("Router iniciado.")
    print(f"- Buscando imagen: {CFG.template_copiado_path}")
    print("- Cuando aparezca 'Copiado', leeré el portapapeles y enfocaré CMD / PowerShell / Sublime.\n")

    last_action_ts = 0.0
    last_clip = ""

    while True:
        found = wait_for_copiado_image(CFG.template_copiado_path, CFG.image_confidence)
        now = time.time()

        if found and (now - last_action_ts) > CFG.cooldown_s:
            try:
                clip = pyperclip.paste()
            except Exception:
                clip = ""

            clip = clip or ""
            if clip.strip() and clip != last_clip:
                last_clip = clip
                last_action_ts = now

                target = classify_target(clip)
                print(f"[{time.strftime('%H:%M:%S')}] Detectado 'Copiado' -> destino: {target}")

                handle_clipboard_routing(clip)

        time.sleep(CFG.poll_interval_s)


if __name__ == "__main__":
    pyautogui.FAILSAFE = True
    main()
