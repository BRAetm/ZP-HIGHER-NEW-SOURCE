"""
EngineThread — Threaded engine runner for ZP HIGHER
Reconstructed from exe diagnostic output
CLASS EngineThread: PaintDeviceMetric,RenderFlag,acceptDrops,...
"""

from PySide6.QtCore import QThread, Signal, QObject
from engine import Engine

C_TEXT = "#e0e0e0"
C_SUCCESS = "#00d2d3"
C_ERROR = "#ff4757"


class EngineThread(QThread):
    """Runs the detection engine in a separate thread."""

    status_update = Signal(str, str)  # status, color
    shot_fired = Signal(float, bool)  # fill_pct, in_green
    error_occurred = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.engine = None
        self._running = False

    def run(self):
        """Thread entry point — starts the engine."""
        self._running = True
        try:
            self.engine = Engine(fps=240)
            ok = self.engine.start()
            if not ok:
                self.error_occurred.emit("Engine start failed")
                return

            self.status_update.emit("Running", C_SUCCESS)
            self.engine.run_loop(fire_callback=self._on_shot)

        except Exception as e:
            self.error_occurred.emit(str(e))
        finally:
            if self.engine:
                self.engine.stop()
            self.status_update.emit("Stopped", C_ERROR)

    def stop(self):
        """Request engine stop."""
        self._running = False
        if self.engine:
            self.engine.stop()
        self.wait()

    def _on_shot(self, fill_pct: float, in_green: bool):
        """Called when engine detects a shot."""
        self.shot_fired.emit(fill_pct, in_green)
