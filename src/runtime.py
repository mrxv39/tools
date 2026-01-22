import queue
import threading
import time

from src.input_listeners import InputListeners
from src.router_worker import RouterWorker


class RouterRuntime:
    def __init__(self, cfg):
        self.cfg = cfg
        self._running = False

        self._q = queue.Queue(maxsize=5)
        self._worker_thread = None

        self._listeners = None
        self._worker = RouterWorker(cfg)

    def is_running(self) -> bool:
        return self._running

    def start(self):
        if self._running:
            return
        self._running = True

        self._worker_thread = threading.Thread(target=self._worker_loop, daemon=True)
        self._worker_thread.start()

        self._listeners = InputListeners(
            running_fn=self.is_running,
            enqueue_click_fn=self._enqueue_click,
            on_stop_fn=self.stop,
            debug=self.cfg.debug,
        )
        self._listeners.start()

    def stop(self):
        if not self._running:
            return
        self._running = False

        try:
            if self._listeners:
                self._listeners.stop()
        except Exception:
            pass

    def _enqueue_click(self, x: int, y: int, ts: float):
        try:
            self._q.put_nowait((int(x), int(y), float(ts)))
        except queue.Full:
            if self.cfg.debug:
                print("  [DBG] queue full: drop click")

    def _worker_loop(self):
        while self._running:
            try:
                x, y, ts = self._q.get(timeout=0.2)
            except queue.Empty:
                continue

            try:
                self._worker.process_click(x, y, ts)
            finally:
                try:
                    self._q.task_done()
                except Exception:
                    pass
            time.sleep(0.0)
