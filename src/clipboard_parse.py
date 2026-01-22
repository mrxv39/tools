# C:\Users\Usuario\tools\chatgpt_router\src\clipboard_parse.py
import os
import re
from dataclasses import dataclass


@dataclass
class ClipboardPayload:
    file_path: str | None
    project_folder: str | None
    content: str


# Comentarios típicos por lenguaje
COMMENT_PREFIXES = [
    "#",     # Python, Bash
    "//",    # C, JS, Java
    ";",     # ini, asm
    "--",    # SQL, Lua
]


WIN_PATH_RE = re.compile(r"^[A-Za-z]:\\")
LINUX_PATH_RE = re.compile(r"^/")


def strip_comment(line: str) -> str:
    """
    Quita prefijos de comentario si existen.
    """
    s = line.strip()
    for pref in COMMENT_PREFIXES:
        if s.startswith(pref):
            s = s[len(pref):].strip()
            break
    return s


def looks_like_path(path: str) -> bool:
    """
    Detecta si parece una ruta Windows o Linux.
    """
    if WIN_PATH_RE.match(path):
        return True
    if LINUX_PATH_RE.match(path):
        return True
    return False


def normalize_path(path: str) -> str:
    """
    Normaliza la ruta según el SO local.
    Si viene Linux y estás en Windows, la deja como está (solo limpia).
    """
    path = path.strip().strip('"').strip("'")
    path = path.replace("/", os.sep).replace("\\", os.sep)
    return os.path.normpath(path)


def parse_clipboard(text: str) -> ClipboardPayload:
    """
    Si la primera línea NO vacía contiene una ruta (aunque esté comentada),
    la usa como file_path.
    """
    text = text or ""
    lines = text.replace("\r\n", "\n").replace("\r", "\n").split("\n")

    first_nonempty_idx = None
    first_line = ""

    for i, ln in enumerate(lines):
        if ln.strip():
            first_nonempty_idx = i
            first_line = ln.strip()
            break

    if first_nonempty_idx is None:
        return ClipboardPayload(None, None, "")

    # Limpia comentario
    cleaned = strip_comment(first_line)

    if looks_like_path(cleaned):
        file_path = normalize_path(cleaned)

        # Project folder
        project_folder = os.path.dirname(file_path)

        # El contenido es todo lo que sigue
        rest_lines = lines[first_nonempty_idx + 1:]

        # Quita líneas vacías iniciales
        while rest_lines and not rest_lines[0].strip():
            rest_lines.pop(0)

        content = "\n".join(rest_lines)

        return ClipboardPayload(
            file_path=file_path,
            project_folder=project_folder,
            content=content
        )

    # Si no era ruta, todo el texto es contenido
    return ClipboardPayload(
        file_path=None,
        project_folder=None,
        content=text
    )
