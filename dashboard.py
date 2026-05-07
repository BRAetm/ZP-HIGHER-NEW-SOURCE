"""
Dashboard — Main dashboard widget for ZP HIGHER
Reconstructed from exe diagnostic output (diag2.txt)
CLASS Dashboard: PaintDeviceMetric,RenderFlag,acceptDrops,accessibleDescription,
  accessibleIdentifier,accessibleName,actionEvent,actions,activateWindow,
  addAction,addActions,adjustSize,autoFillBackground,backgroundRole,backingStore,
  baseSize,blockSignals,changeEvent,childAt,childEvent,children,childrenRect,childrenRegi
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QColor

# Color constants from diag.txt
C_BG = "#1a1a2e"
C_BLUE = "#16213e"
C_BLUE2 = "#0f3460"
C_BORDER = "#533483"
C_BORDER_PURPLE = "#7b2d8e"
C_CARD = "#1e1e3a"
C_ERROR = "#ff4757"
C_PURPLE = "#6c5ce7"
C_PURPLE2 = "#a29bfe"
C_PURPLE_GLOW = "#b388ff"
C_RED = "#ff6b6b"
C_SUCCESS = "#00d2d3"
C_TEXT = "#e0e0e0"
C_TEXT2 = "#a0a0a0"
C_TEXT3 = "#808080"
C_WARNING = "#ffa502"


class Dashboard(QWidget):
    """Main dashboard widget showing shot stats, calibration, and status."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAutoFillBackground(True)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Title
        title = QLabel("ZP HIGHER Dashboard")
        title.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {C_PURPLE2}; padding-bottom: 10px;")
        layout.addWidget(title)

        # Stats cards
        cards_layout = QHBoxLayout()

        self.card_shots = GlassCard("Total Shots", "0", C_BLUE2)
        self.card_accuracy = GlassCard("Accuracy", "0%", C_BLUE2)
        self.card_calibration = GlassCard("Calibration", "N/A", C_BLUE2)

        cards_layout.addWidget(self.card_shots)
        cards_layout.addWidget(self.card_accuracy)
        cards_layout.addWidget(self.card_calibration)
        layout.addLayout(cards_layout)

        # Status section
        status_frame = QFrame()
        status_frame.setFrameShape(QFrame.Shape.StyledPanel)
        status_frame.setStyleSheet(f"background-color: {C_CARD}; border: 1px solid {C_BORDER}; border-radius: 8px; padding: 10px;")
        status_layout = QVBoxLayout(status_frame)

        self.lbl_status = QLabel("Status: Stopped")
        self.lbl_status.setStyleSheet(f"color: {C_TEXT}; font-size: 14px;")
        status_layout.addWidget(self.lbl_status)

        self.lbl_last_shot = QLabel("Last Shot: —")
        self.lbl_last_shot.setStyleSheet(f"color: {C_TEXT2}; font-size: 12px;")
        status_layout.addWidget(self.lbl_last_shot)

        layout.addWidget(status_frame)
        layout.addStretch()

    def update_stats(self, shots: int, accuracy: float, calibration: str):
        """Update dashboard statistics."""
        self.card_shots.set_value(str(shots))
        self.card_accuracy.set_value(f"{accuracy:.1f}%")
        self.card_calibration.set_value(calibration)

    def update_status(self, status: str, color: str = C_TEXT):
        """Update status text."""
        self.lbl_status.setText(f"Status: {status}")
        self.lbl_status.setStyleSheet(f"color: {color}; font-size: 14px;")

    def update_last_shot(self, fill_pct: float, in_green: bool):
        """Update last shot info."""
        ts = "🟢" if in_green else "⚪"
        self.lbl_last_shot.setText(f"Last Shot: {fill_pct:.1%} {ts}")
