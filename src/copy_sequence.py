from src.copiado_detector import find_within_window_near_click, wait_until_absent_near_click


def wait_and_find_copiado_after_copiarcodigo(cfg, x: int, y: int) -> bool:
    """
    Secuencia:
      1) Buscar copiarcodigo.png cerca del click
      2) Si está, esperar a que desaparezca
      3) Buscar copiado.png
    Fallback:
      - Si no se detecta copiarcodigo.png, buscar directamente copiado.png
    """
    saw_copy_button = find_within_window_near_click(
        template_path=cfg.template_copiarcodigo_path,
        confidence=cfg.image_confidence,
        window_s=cfg.copy_button_search_window_s,
        poll_s=cfg.search_poll_interval_s,
        click_x=int(x),
        click_y=int(y),
        half_box_px=cfg.half_box_px,
        debug=cfg.debug,
        debug_screenshots=cfg.debug_screenshots,
        debug_dir=cfg.debug_dir,
    )

    if saw_copy_button:
        if cfg.debug:
            print("  [DBG] copiarcodigo FOUND -> waiting disappear")

        wait_until_absent_near_click(
            template_path=cfg.template_copiarcodigo_path,
            confidence=cfg.image_confidence,
            window_s=cfg.copy_button_disappear_window_s,
            poll_s=cfg.search_poll_interval_s,
            click_x=int(x),
            click_y=int(y),
            half_box_px=cfg.half_box_px,
            debug=cfg.debug,
            debug_screenshots=cfg.debug_screenshots,
            debug_dir=cfg.debug_dir,
        )

    return find_within_window_near_click(
        template_path=cfg.template_copiado_path,
        confidence=cfg.image_confidence,
        window_s=cfg.search_window_s,
        poll_s=cfg.search_poll_interval_s,
        click_x=int(x),
        click_y=int(y),
        half_box_px=cfg.half_box_px,
        debug=cfg.debug,
        debug_screenshots=cfg.debug_screenshots,
        debug_dir=cfg.debug_dir,
    )
