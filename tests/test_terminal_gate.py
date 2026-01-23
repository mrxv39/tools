from src.terminal_gate import gate_terminal_payload


def test_cmd_transcript_without_close_is_blocked():
    text = """Microsoft Windows [Versión 10.0.19045.6466]
(c) Microsoft Corporation. Todos los derechos reservados.

C:\\Users\\Usuario>git status
fatal: not a git repository (or any of the parent directories): .git

C:\\Users\\Usuario>
"""
    r = gate_terminal_payload(text)
    assert r.should_execute is False


def test_cmd_transcript_with_close_executes_n_minus_1():
    text = """C:\\>echo A
A
C:\\>dir
 Volume in drive C is Windows
 Directory of C:\\

C:\\>echo A
"""
    r = gate_terminal_payload(text)
    assert r.should_execute is True
    assert r.payload == "echo A\ndir"


def test_powershell_transcript_without_close_is_blocked():
    text = """PowerShell 7.5.4
PS C:\\Users\\Usuario> git status
fatal: not a git repository (or any of the parent directories): .git
PS C:\\Users\\Usuario>
"""
    r = gate_terminal_payload(text)
    assert r.should_execute is False


def test_powershell_transcript_with_close_executes_n_minus_1():
    text = """PS C:\\> Get-Process
Handles  NPM(K)    PM(K)      WS(K)     CPU(s)     Id  SI ProcessName
------  ------    -----      -----     ------     --  -- -----------
PS C:\\> Get-Service
Status   Name               DisplayName
------   ----               -----------
PS C:\\> Get-Process
"""
    r = gate_terminal_payload(text)
    assert r.should_execute is True
    assert r.payload == "Get-Process\nGet-Service"


def test_plain_text_single_line_allowed():
    r = gate_terminal_payload("git status")
    assert r.should_execute is True
    assert r.payload == "git status"


def test_plain_text_multiline_without_close_is_blocked():
    r = gate_terminal_payload("echo A\ndir")
    assert r.should_execute is False


def test_plain_text_multiline_with_close_executes_n_minus_1():
    r = gate_terminal_payload("echo A\ndir\necho A")
    assert r.should_execute is True
    assert r.payload == "echo A\ndir"
