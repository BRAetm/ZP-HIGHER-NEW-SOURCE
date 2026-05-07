"""
main_v2.py — Improved PySide6 UI for ZP HIGHER
Production-ready: proper logging, error recovery, clean shutdown, accurate status.
"""

import sys
import logging
import traceback
from typing import Optional

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QCheckBox, QSpinBox, QDoubleSpinBox,
    QGroupBox, QSystemTrayIcon, QMenu, QMessageBox
)
from PySide6.QtCore import Qt, QTimer, Signal, QObject
from PySide6.QtGui import QIcon, QAction

logging.basicConfig(
    level=logging.INFO,
    format='[MAIN] %(asctime)s %(levelname)s: %(message)s',
    datefmt='%H:%M:%S'
)
log = logging.getLogger(__name__)

# Import engine and controller with fallback
try:
    from engine_v2 import Engine, BGRMeterDetector
    ENGINE_V2 = True
except ImportError:
    from engine import Engine, BGRMeterDetector
    ENGINE_V2 = False
    log.warning("engine_v2 not found, falling back to engine.py")

try:
    from controller_ps import PSControllerBridge
    CTRL_OK = True
except ImportError:
    CTRL_OK = False
    log.warning("controller_ps not found")


class SignalBus(QObject):
    """Thread-safe signal bus for cross-thread updates."""
    status_update = Signal(str)
    shot_fired = Signal(float, bool)  # fill_pct, in_green
    error_occurred = Signal(str)


class ZPHigherMainWindow(QMainWindow):
    """Main window for ZP HIGHER shot detector."""

    def __init__(self):
        super().__init__()
        self.signal_bus = SignalBus()
        self.engine: Optional[Engine] = None
        self.controller: Optional[PSControllerBridge] = None
        self.tray_icon: Optional[QSystemTrayIcon] = None

        self._setup_ui()
        self._setup_tray()
        self._connect_signals()
        self._init_controller()

        log.info("ZP HIGHER main window initialized")

    def _setup_ui(self):
        self.setWindowTitle("ZP HIGHER — Shot Meter Detector")
        self.setFixedSize(900, 600)
        self.setWindowIcon(QIcon.fromTheme("video-display"))

        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)

        # Left: Shooting controls
        left = QGroupBox("Shooting")
        left_layout = QVBoxLayout(left)
        self.btn_start = QPushButton("▶ Start Engine")
        self.btn_stop = QPushButton("■ Stop Engine")
        self.btn_stop.setEnabled(False)
        self.chk_enabled = QCheckBox("Detector Enabled")
        self.chk_enabled.setChecked(True)
        self.lbl_status = QLabel("Status: Stopped")
        self.lbl_status.setStyleSheet("color: #ff5555; font-weight: bold;")
        self.lbl_calib = QLabel("Calibration: N/A")
        self.lbl_last_shot = QLabel("Last Shot: —")

        left_layout.addWidget(self.chk_enabled)
        left_layout.addWidget(self.btn_start)
        left_layout.addWidget(self.btn_stop)
        left_layout.addSpacing(20)
        left_layout.addWidget(QLabel("Trigger %:"))
        self.spin_trigger = QDoubleSpinBox()
        self.spin_trigger.setRange(0.0, 1.0)
        self.spin_trigger.setValue(0.95)
        self.spin_trigger.setSingleStep(0.01)
        left_layout.addWidget(self.spin_trigger)
        left_layout.addSpacing(20)
        left_layout.addWidget(self.lbl_status)
        left_layout.addWidget(self.lbl_calib)
        left_layout.addWidget(self.lbl_last_shot)
        left_layout.addStretch()

        # Middle: Features
        mid = QGroupBox("Features")
        mid_layout = QVBoxLayout(mid)
        self.chk_defense = QCheckBox("Defense AI")
        self.chk_stamina = QCheckBox("Infinite Stamina")
        self.chk_tempo = QCheckBox("Stick Tempo")
        self.chk_quickstop = QCheckBox("Quickstop")
        self.chk_contest = QCheckBox("Contest Assist")
        mid_layout.addWidget(self.chk_defense)
        mid_layout.addWidget(self.chk_stamina)
        mid_layout.addWidget(self.chk_tempo)
        mid_layout.addWidget(self.chk_quickstop)
        mid_layout.addWidget(self.chk_contest)
        mid_layout.addSpacing(20)
        mid_layout.addWidget(QLabel("Tempo ms:"))
        self.spin_tempo = QSpinBox()
        self.spin_tempo.setRange(10, 100)
        self.spin_tempo.setValue(39)
        mid_layout.addWidget(self.spin_tempo)
        mid_layout.addStretch()

        # Right: System
        right = QGroupBox("System")
        right_layout = QVBoxLayout(right)
        self.lbl_engine = QLabel(f"Engine: {'v2 ✓' if ENGINE_V2 else 'v1 ⚠'}")
        self.lbl_ctrl = QLabel(f"Controller: {'YES ✓' if CTRL_OK else 'NO ⚠'}")
        self.lbl_bettercam = QLabel("BetterCam: —")
        self.lbl_fps = QLabel("FPS: —")
        self.btn_exit = QPushButton("Exit")
        right_layout.addWidget(self.lbl_engine)
        right_layout.addWidget(self.lbl_ctrl)
        right_layout.addWidget(self.lbl_bettercam)
        right_layout.addWidget(self.lbl_fps)
        right_layout.addSpacing(20)
        right_layout.addWidget(self.btn_exit)
        right_layout.addStretch()

        main_layout.addWidget(left)
        main_layout.addWidget(mid)
        main_layout.addWidget(right)

    def _setup_tray(self):
        if not QSystemTrayIcon.isSystemTrayAvailable():
            return
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(QIcon.fromTheme("video-display"))
        tray_menu = QMenu()
        show_action = QAction("Show", self)
        hide_action = QAction("Hide", self)
        exit_action = QAction("Exit", self)
        show_action.triggered.connect(self.show)
        hide_action.triggered.connect(self.hide)
        exit_action.triggered.connect(self.close)
        tray_menu.addAction(show_action)
        tray_menu.addAction(hide_action)
        tray_menu.addSeparator()
        tray_menu.addAction(exit_action)
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()

    def _connect_signals(self):
        self.btn_start.clicked.connect(self.start_engine)
        self.btn_stop.clicked.connect(self.stop_engine)
        self.btn_exit.clicked.connect(self.close)
        self.spin_trigger.valueChanged.connect(self._update_trigger)
        self.chk_defense.toggled.connect(self._toggle_defense)
        self.chk_tempo.toggled.connect(self._toggle_tempo)
        self.chk_quickstop.toggled.connect(self._toggle_quickstop)
        self.signal_bus.status_update.connect(self.lbl_status.setText)
        self.signal_bus.shot_fired.connect(self._on_shot_fired)
        self.signal_bus.error_occurred.connect(self._on_error)

    def _init_controller(self):
        if not CTRL_OK:
            return
        try:
            self.controller = PSControllerBridge()
            self.controller.start()
            log.info("Controller bridge started")
        except Exception as e:
            log.error(f"Controller init failed: {e}")
            self.controller = None

    def start_engine(self):
        if self.engine and self.engine.running:
            return
        try:
            self.engine = Engine(fps=240)
            ok = self.engine.start()
            if not ok:
                self.signal_bus.error_occurred.emit("Engine start failed")
                return
            self.btn_start.setEnabled(False)
            self.btn_stop.setEnabled(True)
            self.lbl_status.setText("Status: Running")
            self.lbl_status.setStyleSheet("color: #55ff55; font-weight: bold;")
            self.lbl_bettercam.setText("BetterCam: YES ✓")

            # Start detection loop in timer (runs in Qt thread)
            self._detect_timer = QTimer()
            self._detect_timer.timeout.connect(self._run_detection)
            self._detect_timer.start(4)  # ~240 FPS

            log.info("Engine started from UI")
        except Exception as e:
            log.error(f"Start engine error: {e}")
            self.signal_bus.error_occurred.emit(str(e))

    def stop_engine(self):
        if self.engine:
            self.engine.stop()
        self.btn_start.setEnabled(True)
        self.btn_stop.setEnabled(False)
        self.lbl_status.setText("Status: Stopped")
        self.lbl_status.setStyleSheet("color: #ff5555; font-weight: bold;")
        if hasattr(self, '_detect_timer'):
            self._detect_timer.stop()
        log.info("Engine stopped from UI")

    def _run_detection(self):
        if not self.engine or not self.engine.running:
            return
        frame = self.engine.cam.get_latest_frame() if self.engine.cam else None
        if frame is None:
            return
        result = self.engine.detector.detect_meter(frame)
        if result:
            fill_pct, in_green = result
            self.engine.detector.calibrate(fill_pct)
            if fill_pct >= self.engine.detector.trigger_pct:
                self.signal_bus.shot_fired.emit(fill_pct, in_green)
                if self.controller:
                    self.controller.fire_shot(
                        tempo=self.chk_tempo.isChecked(),
                        tempo_ms=self.spin_tempo.value()
                    )
            # Update UI
            self.lbl_calib.setText(f"Calibration: {fill_pct:.1%}")
            status = f"FPS: {self.engine.target_fps} | Peak: {self.engine.detector.peak_threshold:.1%}"
            self.lbl_fps.setText(status)

    def _on_shot_fired(self, fill_pct: float, in_green: bool):
        ts = time.strftime("%H:%M:%S")
        green_str = "🟢 GREEN" if in_green else "⚪ normal"
        self.lbl_last_shot.setText(f"Last Shot: {ts} @ {fill_pct:.1%} {green_str}")
        log.info(f"Shot fired: {fill_pct:.1%} {green_str}")

    def _on_error(self, msg: str):
        log.error(f"UI error: {msg}")
        QMessageBox.critical(self, "Error", msg)

    def _update_trigger(self, val: float):
        if self.engine:
            self.engine.detector.trigger_pct = val

    def _toggle_defense(self, on: bool):
        if self.controller:
            self.controller.defense_enabled = on

    def _toggle_tempo(self, on: bool):
        if self.controller:
            self.controller.stick_tempo_enabled = on

    def _toggle_quickstop(self, on: bool):
        if self.controller:
            self.controller.quickstop_enabled = on

    def closeEvent(self, event):
        self.stop_engine()
        if self.controller:
            self.controller.stop()
        if self.tray_icon:
            self.tray_icon.hide()
        log.info("Application shutdown complete")
        event.accept()


if __name__ == "__main__":
    try:
        app = QApplication(sys.argv)
        window = ZPHigherMainWindow()
        window.show()
        sys.exit(app.exec())
    except Exception as e:
        log.critical(f"Fatal error: {e}\n{traceback.format_exc()}")
        sys.exit(1)
