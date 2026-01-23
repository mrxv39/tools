import re
from dataclasses import dataclass


@dataclass(frozen=True)
class TerminalGateResult:
    """Result of gating a clipboard payload before terminal execution."""
    should_execute: bool
    payload: str
    reason: str


_CMD_PROMPT_RE = re.compile(r"^(?P<prompt>[A-Za-z]:\\[^>]*>)\s*(?P<cmd>.*)$")
_PS_PROMPT_RE = re.compile(r"^(?P<prompt>PS\s+[^>]*>)\s*(?P<cmd>.*)$")


def _extract_cmd_from_prompt_line(line: str) -> str | None:
    """Return the command part of a CMD prompt line, or None if it's not a prompt line."""
    m = _CMD_PROMPT_RE.match(line.rstrip("\r\n"))
    if not m:
        return None
    cmd = (m.group("cmd") or "").strip()
    return cmd or ""


def _extract_cmd_from_powershell_prompt_line(line: str) -> str | None:
    """Return the command part of a PowerShell prompt line, or None if it's not a prompt line."""
    m = _PS_PROMPT_RE.match(line.rstrip("\r\n"))
    if not m:
        return None
    cmd = (m.group("cmd") or "").strip()
    return cmd or ""


def _gate_commands(commands: list[str], kind: str, *, allow_single: bool) -> TerminalGateResult:
    """Apply the close-marker rule to a list of *real* commands."""
    real = [c.strip() for c in commands if c.strip()]
    if not real:
        return TerminalGateResult(False, "", f"{kind}: no commands found")

    if len(real) == 1:
        if allow_single:
            return TerminalGateResult(True, real[0], f"{kind}: single command allowed")
        return TerminalGateResult(False, "", f"{kind}: blocked (missing close marker)")

    first = real[0]
    last = real[-1]
    if first != last:
        return TerminalGateResult(
            False,
            "",
            f"{kind}: blocked (missing close marker: first command != last command)",
        )

    to_run = real[:-1]  # drop close marker (not executed)
    if not to_run:
        return TerminalGateResult(False, "", f"{kind}: blocked (only close marker present)")

    return TerminalGateResult(True, "\n".join(to_run), f"{kind}: ok (close marker present)")


def gate_terminal_payload(text: str) -> TerminalGateResult:
    """Gate clipboard text before running in a terminal.

    Rules:
      - Terminal transcripts (CMD/PowerShell): execute only if the first real command
        repeats as the last real command; the last repetition is a close marker and
        is NOT executed.
      - Plain text (not a transcript):
          * single line -> allowed
          * multi-line -> same close-marker rule (first == last), last not executed
    """
    normalized_text = text.replace("\r\n", "\n").replace("\r", "\n")
    raw_lines = normalized_text.split("\n")
    lines = [ln for ln in raw_lines if ln is not None]

    # Detect CMD transcript: any prompt line "C:\...>".
    cmd_commands: list[str] = []
    saw_cmd_prompt = False
    for ln in lines:
        cmd_part = _extract_cmd_from_prompt_line(ln)
        if cmd_part is None:
            continue
        saw_cmd_prompt = True
        if cmd_part.strip():
            cmd_commands.append(cmd_part)
    if saw_cmd_prompt:
        return _gate_commands(cmd_commands, "cmd", allow_single=False)

    # Detect PowerShell transcript: prompt lines "PS ...>".
    ps_commands: list[str] = []
    saw_ps_prompt = False
    for ln in lines:
        cmd_part = _extract_cmd_from_powershell_prompt_line(ln)
        if cmd_part is None:
            continue
        saw_ps_prompt = True
        if cmd_part.strip():
            ps_commands.append(cmd_part)
    if saw_ps_prompt:
        return _gate_commands(ps_commands, "powershell", allow_single=False)

    # Plain text.
    non_empty = [ln.strip() for ln in lines if ln.strip()]
    if not non_empty:
        return TerminalGateResult(False, "", "plain: empty")
    if len(non_empty) == 1:
        line = non_empty[0]
        if normalized_text.endswith("\n"):
            return TerminalGateResult(True, line + "\n", "plain: single line allowed")
        return TerminalGateResult(True, line, "plain: single line allowed")

    return _gate_commands(non_empty, "plain", allow_single=False)
