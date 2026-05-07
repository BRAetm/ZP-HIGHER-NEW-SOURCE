"""
GlassCard — Frosted glass card widget for ZP HIGHER
Reconstructed from exe diagnostic output
CLASS GlassCard: PaintDeviceMetric,RenderFlag,Shadow,Shape,StyleMask,acceptDrops,...
"""

from PySide6.QtWidgets import QFrame, QVBoxLayout, QLabel
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QColor

C_CARD = "#1e1e3a"
C_BORDER = "#533483"
C_PURPLE2 = "#a29bfe"
C_TEXT = "#e0e0e0"


class GlassCard(QFrame):
    """Frosted glass card with title and value display."""

    def __init__(self, title: str, value: str, bg_color: str = C_CARD, parent=None):
        super().__init__(parent)
        self.title = title
        self.value = value
        self.bg_color = bg_color
        self._setup_ui()

    def _setup_ui(self):
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setStyleSheet(f"""
            GlassCard {{
                background-color: {self.bg_color};
                border: 1px solid {C_BORDER};
                border-radius: 12px;
                padding: 15px;
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(8)

        self.lbl_title = QLabel(self.title)
        self.lbl_title.setFont(QFont("Arial", 10))
        self.lbl_title.setStyleSheet(f"color: {C_PURPLE2};")
        layout.addWidget(self.lbl_title)

        self.lbl_value = QLabel(self.value)
        self.lbl_value.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        self.lbl_value.setStyleSheet(f"color: {C_TEXT};")
        layout.addWidget(self.lbl_value)

        layout.addStretch()

    def set_value(self, value: str):
        """Update the displayed value."""
        self.value = value
        self.lbl_value.setText(value)

    def set_title(self, title: str):
        """Update the card title."""
        self.title = title
        self.lbl_title.setText(title)
