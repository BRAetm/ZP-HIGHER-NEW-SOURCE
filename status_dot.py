"""
StatusDot — Colored status indicator dot
Reconstructed from exe diagnostic output
CLASS StatusDot: PaintDeviceMetric,RenderFlag,acceptDrops,...
"""

from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QPainter, QColor, QBrush

C_SUCCESS = "#00d2d3"
C_ERROR = "#ff4757"
C_WARNING = "#ffa502"
C_TEXT2 = "#a0a0a0"


class StatusDot(QWidget):
    """Colored dot indicating status (green=active, red=error, gray=inactive)."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._color = QColor(C_TEXT2)
        self.setFixedSize(12, 12)

    def set_status(self, status: str):
        """Set status: 'active', 'error', 'warning', 'inactive'."""
        colors = {
            'active': C_SUCCESS,
            'error': C_ERROR,
            'warning': C_WARNING,
            'inactive': C_TEXT2,
        }
        self._color = QColor(colors.get(status, C_TEXT2))
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setBrush(QBrush(self._color))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(0, 0, self.width(), self.height())
