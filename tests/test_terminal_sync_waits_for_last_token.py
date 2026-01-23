import src.terminal_sync as ts


def test_wait_until_done_token_ignores_old_token_not_at_end(monkeypatch):
    """
    Caso real:
    - El buffer del terminal YA contiene __CHATGPT_ROUTER_DONE__ de una corrida anterior.
    - Mientras corre un comando largo (timeout), el token viejo sigue estando en el texto copiado,
      pero NO es el "último token" del buffer.
    Esperado:
    - NO debe considerarse terminado hasta que el token aparezca al FINAL (últimas líneas).
    """

    snapshots = [
        # 1) Token viejo existe, pero NO es el final del output (ya empezó un comando nuevo)
        "\n".join(
            [
                "old output...",
                ts.DONE_TOKEN,
                r"C:\Users\Usuario\tools\chatgpt_router>echo START",
                "START",
                r"C:\Users\Usuario\tools\chatgpt_router>timeout /t 3",
                "Esperando 3 segundos, presione una tecla para continuar ...",
                "",
            ]
        ),
        # 2) Sigue corriendo: todavía no aparece el token nuevo al final
        "\n".join(
            [
                "old output...",
                ts.DONE_TOKEN,
                r"C:\Users\Usuario\tools\chatgpt_router>echo START",
                "START",
                r"C:\Users\Usuario\tools\chatgpt_router>timeout /t 3",
                "Esperando 2 segundos, presione una tecla para continuar ...",
                "",
            ]
        ),
        # 3) Terminó: aparece el token AL FINAL (nuevo sentinel ejecutado al final del payload)
        "\n".join(
            [
                "old output...",
                ts.DONE_TOKEN,
                r"C:\Users\Usuario\tools\chatgpt_router>echo START",
                "START",
                r"C:\Users\Usuario\tools\chatgpt_router>timeout /t 3",
                "Esperando 1 segundos, presione una tecla para continuar ...",
                r"C:\Users\Usuario\tools\chatgpt_router>",
                ts.DONE_TOKEN,
                "",
            ]
        ),
    ]

    state = {"i": 0, "clipboard": ""}

    def fake_copy_all_fn():
        idx = min(state["i"], len(snapshots) - 1)
        state["clipboard"] = snapshots[idx]
        state["i"] += 1

    def fake_paste():
        return state["clipboard"]

    monkeypatch.setattr(ts.pyperclip, "paste", fake_paste)

    # Evitar sleeps reales
    monkeypatch.setattr(ts.time, "sleep", lambda *_args, **_kwargs: None)

    out = ts.wait_until_done_token_in_clipboard(
        copy_all_fn=fake_copy_all_fn,
        timeout_s=10.0,
        poll_s=0.0,
    )

    # Debe haber esperado hasta el snapshot 3 (al menos 3 iteraciones)
    assert state["i"] >= 3
    assert out.endswith(ts.DONE_TOKEN + "\n") or out.endswith(ts.DONE_TOKEN)


def test_strip_done_token_removes_all_token_lines():
    raw = "\n".join(
        [
            "A",
            ts.DONE_TOKEN,
            "B",
            f"noise {ts.DONE_TOKEN} noise",
            "C",
            "",
        ]
    )
    cleaned = ts._strip_done_token(raw)
    assert ts.DONE_TOKEN not in cleaned
    assert "A" in cleaned
    assert "B" in cleaned
    assert "C" in cleaned
