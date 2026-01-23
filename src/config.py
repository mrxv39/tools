
from dataclasses import dataclass


@dataclass
class Config:
    template_copiado_path: str = r".\copiado.png"
    template_copiarcodigo_path: str = r".\copiarcodigo.png"

    image_confidence: float = 0.78

    search_window_s: float = 1.0
    copy_button_search_window_s: float = 0.35
    copy_button_disappear_window_s: float = 1.50

    search_poll_interval_s: float = 0.10

    cooldown_s: float = 0.25
    press_enter_in_terminal: bool = False

    copy_terminal_text_to_clipboard: bool = True

    # sincronización por sentinel (sin sleep fijo)
    terminal_done_timeout_s: float = 60.0
    terminal_done_poll_s: float = 0.20

    cmd_title_contains: tuple = ("Command Prompt", "cmd.exe", "Símbolo del sistema")
    powershell_title_contains: tuple = ("Windows PowerShell", "PowerShell", "pwsh", "Terminal")
    sublime_title_contains: tuple = ("Sublime Text",)

    cmd_launch: list | None = None
    powershell_launch: list | None = None
    sublime_launch: list | None = None

    debug: bool = True
    debug_screenshots: bool = True
    debug_dir: str = r".\debug_shots"

    half_box_px: int = 50


def load_config() -> Config:
    return Config(
        template_copiado_path=r".\copiado.png",
        template_copiarcodigo_path=r".\copiarcodigo.png",
        image_confidence=0.78,
        search_window_s=1.0,
        copy_button_search_window_s=0.35,
        copy_button_disappear_window_s=1.50,
        search_poll_interval_s=0.10,
        cooldown_s=0.25,
        press_enter_in_terminal=False,
        copy_terminal_text_to_clipboard=True,
        terminal_done_timeout_s=60.0,
        terminal_done_poll_s=0.20,
        cmd_launch=["cmd.exe"],
        powershell_launch=["powershell.exe"],
        sublime_launch=[r"C:\Program Files\Sublime Text\sublime_text.exe"],
        debug=True,
        debug_screenshots=True,
        debug_dir=r".\debug_shots",
        half_box_px=50,
    )
