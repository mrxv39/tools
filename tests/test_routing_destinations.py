from src.config import load_config
from src.route_actions import route_payload


def _force_target(monkeypatch, target_value: str):
    import src.route_actions as ra
    monkeypatch.setattr(ra, "classify_target", lambda _text: target_value)


def _patch_clipboard(monkeypatch):
    import src.terminal_runner as tr

    calls = {
        "with_clip": 0,
        "paste": 0,
        "last_text": None,
        "last_enter": None,
    }

    def _with_clip(text, fn):
        calls["with_clip"] += 1
        calls["last_text"] = text
        return fn()

    def _paste(press_enter=False):
        calls["paste"] += 1
        calls["last_enter"] = press_enter

    monkeypatch.setattr(tr, "with_temporary_clipboard", _with_clip)
    monkeypatch.setattr(tr, "paste_into_active_window", _paste)

    return calls


def _patch_terminal_copy(monkeypatch):
    import src.terminal_runner as tr

    calls = {"copy_all": 0}

    def _copy_all():
        calls["copy_all"] += 1

    monkeypatch.setattr(tr, "copy_all_text_from_active_window_to_clipboard", _copy_all)
    return calls


def _patch_popen(monkeypatch):
    import src.terminal_runner as tr

    calls = {"n": 0, "args": None}

    def _fake_popen(args, **kwargs):
        calls["n"] += 1
        calls["args"] = args

        class _P:
            ...

        return _P()

    monkeypatch.setattr(tr.subprocess, "Popen", _fake_popen)
    monkeypatch.setattr(tr.time, "sleep", lambda _s: None)

    return calls


def test_non_terminal_without_path_is_blocked(monkeypatch):
    _force_target(monkeypatch, "sublime")  # cualquier cosa que NO sea cmd/powershell

    import src.route_actions as ra
    alert_calls = {"n": 0}

    def _fake_alert(_t, _m):
        alert_calls["n"] += 1

    monkeypatch.setattr(ra, "show_alert", _fake_alert)

    cfg = load_config()
    cfg.debug = False

    route_payload(cfg, "def fail(): pass\n", None, None)

    assert alert_calls["n"] == 1


def test_non_terminal_creates_file_and_writes_content(monkeypatch, tmp_path):
    _force_target(monkeypatch, "sublime")

    cfg = load_config()
    cfg.debug = False

    f = tmp_path / "nested" / "new.py"
    assert not f.exists()

    payload = "print('hola')\n"
    route_payload(cfg, payload, str(f), str(f.parent))

    assert f.exists()
    assert f.read_text(encoding="utf-8").replace("\r\n", "\n") == payload


def test_non_terminal_overwrites_existing_file(monkeypatch, tmp_path):
    _force_target(monkeypatch, "sublime")

    cfg = load_config()
    cfg.debug = False

    f = tmp_path / "ok.py"
    f.write_text("old\n", encoding="utf-8")

    payload = "new content\nline2\n"
    route_payload(cfg, payload, str(f), str(tmp_path))

    assert f.read_text(encoding="utf-8").replace("\r\n", "\n") == payload


def test_cmd_always_opens_new_window_and_copies_terminal_to_clipboard(monkeypatch):
    _force_target(monkeypatch, "cmd")
    calls = _patch_clipboard(monkeypatch)
    term = _patch_terminal_copy(monkeypatch)
    popen = _patch_popen(monkeypatch)

    cfg = load_config()
    cfg.debug = False
    cfg.press_enter_in_terminal = True
    cfg.copy_terminal_text_to_clipboard = True

    cmd_text = "dir\n"
    route_payload(cfg, cmd_text, None, None)

    assert popen["n"] == 1
    assert popen["args"] == ["cmd.exe"]
    assert calls["with_clip"] == 1
    assert calls["paste"] == 1
    assert calls["last_enter"] is True
    assert calls["last_text"].startswith(cmd_text)
    assert "__CHATGPT_ROUTER_DONE__" in calls["last_text"]
    assert term["copy_all"] >= 1


def test_powershell_always_opens_new_window_and_copies_terminal_to_clipboard(monkeypatch):
    _force_target(monkeypatch, "powershell")
    calls = _patch_clipboard(monkeypatch)
    term = _patch_terminal_copy(monkeypatch)
    popen = _patch_popen(monkeypatch)

    cfg = load_config()
    cfg.debug = False
    cfg.press_enter_in_terminal = False
    cfg.copy_terminal_text_to_clipboard = True

    ps_text = "Get-ChildItem\n"
    route_payload(cfg, ps_text, None, None)

    assert popen["n"] == 1
    assert popen["args"] == ["powershell.exe"]
    assert calls["with_clip"] == 1
    assert calls["paste"] == 1
    assert calls["last_text"] == ps_text
    assert calls["last_enter"] is False
    assert term["copy_all"] == 1
