import re
import time

import pyperclip


DONE_TOKEN = "__CHATGPT_ROUTER_DONE__"


def _ensure_trailing_newline(s: str) -> str:
    if not s.endswith("\n"):
        return s + "\n"
    return s


def build_payload_with_sentinel(target: str, user_text: str) -> str:
    """
    target: "cmd" o "powershell"
    Devuelve texto que garantiza imprimir DONE_TOKEN al final.
    """
    base = _ensure_trailing_newline(user_text)

    if target == "cmd":
        return base + f"echo {DONE_TOKEN}\n"

    if target == "powershell":
        return base + f'Write-Output "{DONE_TOKEN}"\n'

    return user_text


def _strip_done_token(text: str) -> str:
    if not text:
        return text
    lines = text.splitlines()
    kept = []
    for ln in lines:
        if DONE_TOKEN in ln:
            continue
        kept.append(ln)
    return "\n".join(kept).rstrip() + ("\n" if text.endswith("\n") else "")


_PROMPT_LINE_RE = re.compile(
    r"""^(
        (?:[A-Za-z]:\\.*?>\s*)            # CMD: C:\path>
        |(?:PS\s+.*?>\s*)                 # PowerShell: PS C:\path>
    )$""",
    re.VERBOSE,
)


def _is_prompt_or_blank(line: str) -> bool:
    s = (line or "").rstrip()
    if not s:
        return True
    return bool(_PROMPT_LINE_RE.match(s))


def _done_token_is_last_meaningful_thing(text: str) -> bool:
    """
    Evita falso positivo: solo consideramos DONE si el ÚLTIMO token no tiene output real después.
    Permitimos solo prompt(s) o líneas en blanco después del token.
    """
    if not text:
        return False

    lines = text.splitlines()
    last_idx = None
    for i, ln in enumerate(lines):
        if DONE_TOKEN in ln:
            last_idx = i

    if last_idx is None:
        return False

    tail = lines[last_idx + 1 :]
    for ln in tail:
        if _is_prompt_or_blank(ln):
            continue
        return False
    return True


def wait_until_done_token_in_clipboard(
    copy_all_fn,
    timeout_s: float,
    poll_s: float,
) -> str:
    t0 = time.time()
    last = ""

    while True:
        copy_all_fn()
        try:
            last = pyperclip.paste() or ""
        except Exception:
            last = ""

        if _done_token_is_last_meaningful_thing(last):
            return last

        if (time.time() - t0) >= float(timeout_s):
            return last

        time.sleep(float(poll_s))


def copy_terminal_output_until_done(
    copy_all_fn,
    timeout_s: float,
    poll_s: float,
) -> str:
    raw = wait_until_done_token_in_clipboard(copy_all_fn, timeout_s, poll_s)
    cleaned = _strip_done_token(raw)
    try:
        pyperclip.copy(cleaned)
    except Exception:
        pass
    return cleaned
