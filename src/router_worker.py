import time

from src.active_window import is_active_window_browser
from src.clipboard_io import safe_paste_clipboard
from src.clipboard_parse import parse_clipboard
from src.copy_sequence import wait_and_find_copiado_after_copiarcodigo
from src.route_actions import route_payload


class RouterWorker:
    def __init__(self, cfg):
        self.cfg = cfg
        self._last_action_ts = 0.0
        self._last_seen_clip = ""

    def process_click(self, x: int, y: int, ts: float):
        if ts - self._last_action_ts < self.cfg.cooldown_s:
            if self.cfg.debug:
                print("  [DBG] worker: ignored (cooldown)")
            return

        if not is_active_window_browser():
            if self.cfg.debug:
                print("  [DBG] worker: ignored (active window NOT browser)")
            return

        if self.cfg.debug:
            print(f"[{time.strftime('%H:%M:%S')}] click queued x={x} y={y} (browser ok)")

        found = wait_and_find_copiado_after_copiarcodigo(self.cfg, x, y)

        if not found:
            if self.cfg.debug:
                print("  [DBG] worker: image NOT found")
            return

        clip = safe_paste_clipboard(self.cfg)
        if not clip.strip():
            if self.cfg.debug:
                print("  [DBG] worker: clipboard empty")
            return

        if clip == self._last_seen_clip:
            if self.cfg.debug:
                print("  [DBG] worker: clipboard unchanged (ignored)")
            self._last_action_ts = ts
            return

        self._last_seen_clip = clip
        self._last_action_ts = ts

        parsed = parse_clipboard(clip)
        payload_text = parsed.content if parsed.file_path else clip

        if self.cfg.debug and parsed.file_path:
            print(f"  [DBG] parsed file_path={parsed.file_path}")
            print(f"  [DBG] parsed project_folder={parsed.project_folder}")

        route_payload(self.cfg, payload_text, parsed.file_path, parsed.project_folder)
