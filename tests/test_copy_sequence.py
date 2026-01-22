from types import SimpleNamespace

import src.copy_sequence as cs


def test_sequence_when_copy_button_found(monkeypatch):
    calls = []

    def fake_find(*, template_path, **kwargs):
        calls.append(("find", template_path))
        if template_path.endswith("copiarcodigo.png"):
            return True
        if template_path.endswith("copiado.png"):
            return True
        return False

    def fake_wait_absent(*, template_path, **kwargs):
        calls.append(("wait_absent", template_path))
        return True

    monkeypatch.setattr(cs, "find_within_window_near_click", fake_find)
    monkeypatch.setattr(cs, "wait_until_absent_near_click", fake_wait_absent)

    cfg = SimpleNamespace(
        template_copiarcodigo_path=r".\copiarcodigo.png",
        template_copiado_path=r".\copiado.png",
        image_confidence=0.78,
        copy_button_search_window_s=0.35,
        copy_button_disappear_window_s=1.50,
        search_window_s=1.0,
        search_poll_interval_s=0.10,
        half_box_px=50,
        debug=False,
        debug_screenshots=False,
        debug_dir=r".\debug_shots",
    )

    ok = cs.wait_and_find_copiado_after_copiarcodigo(cfg, 100, 100)
    assert ok is True
    assert calls == [
        ("find", r".\copiarcodigo.png"),
        ("wait_absent", r".\copiarcodigo.png"),
        ("find", r".\copiado.png"),
    ]


def test_sequence_when_copy_button_not_found(monkeypatch):
    calls = []

    def fake_find(*, template_path, **kwargs):
        calls.append(("find", template_path))
        if template_path.endswith("copiarcodigo.png"):
            return False
        if template_path.endswith("copiado.png"):
            return True
        return False

    def fake_wait_absent(*, template_path, **kwargs):
        calls.append(("wait_absent", template_path))
        return True

    monkeypatch.setattr(cs, "find_within_window_near_click", fake_find)
    monkeypatch.setattr(cs, "wait_until_absent_near_click", fake_wait_absent)

    cfg = SimpleNamespace(
        template_copiarcodigo_path=r".\copiarcodigo.png",
        template_copiado_path=r".\copiado.png",
        image_confidence=0.78,
        copy_button_search_window_s=0.35,
        copy_button_disappear_window_s=1.50,
        search_window_s=1.0,
        search_poll_interval_s=0.10,
        half_box_px=50,
        debug=False,
        debug_screenshots=False,
        debug_dir=r".\debug_shots",
    )

    ok = cs.wait_and_find_copiado_after_copiarcodigo(cfg, 100, 100)
    assert ok is True
    assert calls == [
        ("find", r".\copiarcodigo.png"),
        ("find", r".\copiado.png"),
    ]
