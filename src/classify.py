import re


_CMD_PROMPT_RE = re.compile(r"^[A-Za-z]:\\[^>]*>\s*\S+")
_PS_PROMPT_RE = re.compile(r"^PS\s+[^>]*>\s*\S+")


def looks_like_cmd_transcript(text: str) -> bool:
    """Detect a copied CMD transcript (prompt lines like C:\\path>)."""
    lines = text.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    return any(_CMD_PROMPT_RE.match(ln.strip()) for ln in lines if ln.strip())


def looks_like_powershell_transcript(text: str) -> bool:
    """Detect a copied PowerShell transcript (prompt lines like PS C:\\path>)."""
    lines = text.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    return any(_PS_PROMPT_RE.match(ln.strip()) for ln in lines if ln.strip())


def looks_like_powershell(text: str) -> bool:
    t = text.strip()

    if looks_like_powershell_transcript(t):
        return True

    ps_cmdlets = [
        r"\bGet-\w+\b",
        r"\bSet-\w+\b",
        r"\bNew-\w+\b",
        r"\bRemove-\w+\b",
        r"\bStart-\w+\b",
        r"\bStop-\w+\b",
        r"\bSelect-Object\b",
        r"\bWhere-Object\b",
        r"\bForEach-Object\b",
        r"\bOut-File\b",
        r"\bFormat-Table\b",
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

    if looks_like_cmd_transcript(t):
        return True

    cmd_starts = [
        r"^\s*(cd|dir|cls|echo|set|type|copy|move|del|erase|rd|rmdir|mkdir|ren|rename)\b",
        r"^\s*(git|pip|python|py|node|npm|npx|yarn|pnpm|docker|kubectl|flyctl|powershell|pwsh)\b",
    ]
    if any(re.search(p, t, re.IGNORECASE) for p in cmd_starts):
        return True

    if re.search(r"(&&|\|\|)\s*\S+", t):
        return True

    if re.search(r"^[A-Za-z]:\\", t) and " " in t:
        return True

    return False


def classify_target(text: str) -> str:
    if looks_like_powershell(text):
        return "powershell"
    if looks_like_cmd(text):
        return "cmd"
    return "sublime"
