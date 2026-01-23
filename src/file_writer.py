from __future__ import annotations

import os

from src.fs_utils import ensure_file_exists


def write_text_file(file_path: str, content: str) -> None:
    """
    Crea el archivo si no existe y luego escribe el contenido (overwrite).
    """
    if not file_path or not str(file_path).strip():
        raise ValueError("file_path vacío en write_text_file()")

    file_path = os.path.normpath(file_path)

    ensure_file_exists(file_path)

    parent = os.path.dirname(file_path)
    if parent:
        os.makedirs(parent, exist_ok=True)

    with open(file_path, "w", encoding="utf-8", newline="\n") as f:
        f.write(content or "")
