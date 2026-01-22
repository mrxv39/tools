import os

from src.config import load_config
from src.route_actions import route_payload


def _force_target(monkeypatch, target_value: str):
    import src.route_actions as ra
    monkeypatch.setattr(ra, "classify_target", lambda _text: target_value)


def _patch_clipboard(monkeypatch):
    import src.route_actions as ra

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

    monkeypatch.setattr(ra, "with_temporary_clipboard", _with_clip)
    monkeypatch.setattr(ra, "paste_into_active_window", _paste)

    return calls


def _patch_sublime_noop(monkeypatch):
    import src.route_actions as ra
    monkeypatch.setattr(ra, "activate_sublime_for_project", lambda *a, **k: True)
    monkeypatch.setattr(ra, "launch_sublime_opening_file", lambda *a, **k: True)


def _patch_popen(monkeypatch):
    import src.route_actions as ra

    calls = {"n": 0, "args": None}

    def _fake_popen(args, **kwargs):
        calls["n"] += 1
        calls["args"] = args
        class _P: ...
        return _P()

    monkeypatch.setattr(ra.subprocess, "Popen", _fake_popen)
    monkeypatch.setattr(ra.time, "sleep", lambda _s: None)

    return calls


def test_sublime_ok_path_exists(monkeypatch, tmp_path):
    _force_target(monkeypatch, "sublime")
    calls = _patch_clipboard(monkeypatch)
    _patch_sublime_noop(monkeypatch)

    cfg = load_config()
    cfg.debug = False

    f = tmp_path / "ok.py"
    f.write_text("", encoding="utf-8")

    payload = "def ok():\n    return 1\n"
    route_payload(cfg, payload, str(f), str(tmp_path))

    assert calls["with_clip"] == 1
    assert calls["paste"] == 1
    assert calls["last_text"] == payload
    assert calls["last_enter"] is False


def test_sublime_without_path_is_blocked(monkeypatch):
    _force_target(monkeypatch, "sublime")
    calls = _patch_clipboard(monkeypatch)
    _patch_sublime_noop(monkeypatch)
    popen = _patch_popen(monkeypatch)

    # NUEVO: debe mostrar alerta
    import src.route_actions as ra
    alert_calls = {"n": 0, "title": None, "msg": None}

    def _fake_alert(title, message):
        alert_calls["n"] += 1
        alert_calls["title"] = title
        alert_calls["msg"] = message

    monkeypatch.setattr(ra, "show_alert", _fake_alert)

    cfg = load_config()
    cfg.debug = False

    route_payload(cfg, "def fail(): pass\n", None, None)

    assert calls["with_clip"] == 0
    assert calls["paste"] == 0
    assert popen["n"] == 0
    assert alert_calls["n"] == 1


def test_sublime_creates_file_if_missing(monkeypatch, tmp_path):
    _force_target(monkeypatch, "sublime")
    calls = _patch_clipboard(monkeypatch)
    _patch_sublime_noop(monkeypatch)

    cfg = load_config()
    cfg.debug = False

    f = tmp_path / "nested" / "new.py"
    assert not f.exists()

    payload = "print('hola')\n"
    route_payload(cfg, payload, str(f), str(f.parent))

    assert f.exists()
    assert calls["with_clip"] == 1
    assert calls["paste"] == 1
    assert calls["last_text"] == payload


def test_cmd_always_opens_new_window(monkeypatch):
    _force_target(monkeypatch, "cmd")
    calls = _patch_clipboard(monkeypatch)
    popen = _patch_popen(monkeypatch)

    cfg = load_config()
    cfg.debug = False
    cfg.press_enter_in_terminal = True

    cmd_text = "dir\n"
    route_payload(cfg, cmd_text, None, None)

    assert popen["n"] == 1
    assert popen["args"] == ["cmd.exe"]
    assert calls["with_clip"] == 1
    assert calls["paste"] == 1
    assert calls["last_text"] == cmd_text
    assert calls["last_enter"] is True


def test_powershell_always_opens_new_window(monkeypatch):
    _force_target(monkeypatch, "powershell")
    calls = _patch_clipboard(monkeypatch)
    popen = _patch_popen(monkeypatch)

    cfg = load_config()
    cfg.debug = False
    cfg.press_enter_in_terminal = False

    ps_text = "Get-ChildItem\n"
    route_payload(cfg, ps_text, None, None)

    assert popen["n"] == 1
    assert popen["args"] == ["powershell.exe"]
    assert calls["with_clip"] == 1
    assert calls["paste"] == 1
    assert calls["last_text"] == ps_text
    assert calls["last_enter"] is False
