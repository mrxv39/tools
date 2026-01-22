from __future__ import annotations

import os


def ensure_file_exists(file_path: str) -> bool:
    """
    Asegura que el archivo exista. Si no existe:
      - crea carpetas padre
      - crea archivo vacío
    Devuelve True si lo creó, False si ya existía.
    """
    if not file_path or not str(file_path).strip():
        raise ValueError("file_path vacío en ensure_file_exists()")

    file_path = os.path.normpath(file_path)

    if os.path.exists(file_path):
        return False

    parent = os.path.dirname(file_path)
    if parent:
        os.makedirs(parent, exist_ok=True)

    with open(file_path, "a", encoding="utf-8"):
        pass

    return True
