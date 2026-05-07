"""
WaveBackground and WaveText — Animated background widgets
Reconstructed from exe diagnostic output
CLASS WaveBackground, WaveText: PaintDeviceMetric,RenderFlag,acceptDrops,...
"""

from PySide6.QtWidgets import QWidget
from PySide6.QtCore import QTimer, Qt, QPropertyAnimation, Property
from PySide6.QtGui import QPainter, QColor, QLinearGradient, QBrush

C_BG = "#1a1a2e"
C_BLUE2 = "#0f3460"
C_PURPLE = "#6c5ce7"
C_PURPLE2 = "#a29bfe"


class WaveBackground(QWidget):
    """Animated wave background effect."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._phase = 0.0
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._update)
        self._timer.start(30)  # ~33 FPS

    def _update(self):
        self._phase += 0.05
        if self._phase > 6.28:
            self._phase = 0.0
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Background gradient
        gradient = QLinearGradient(0, 0, 0, self.height())
        gradient.setColorAt(0.0, QColor(C_BG))
        gradient.setColorAt(1.0, QColor(C_BLUE2))
        painter.fillRect(self.rect(), QBrush(gradient))

        # Animated waves (simplified)
        painter.setPen(QColor(C_PURPLE))
        painter.setBrush(Qt.BrushStyle.NoBrush)

        import math
        for i in range(3):
            points = []
            for x in range(0, self.width(), 10):
                y = self.height()/2 + math.sin(x/100.0 + self._phase + i) * 30
                points.append((x, y))
            # Draw simplified wave
            for j in range(len(points)-1):
                painter.drawLine(points[j][0], int(points[j][1]),
                                points[j+1][0], int(points[j+1][1]))


class WaveText(QWidget):
    """Text with wave animation effect."""

    def __init__(self, text="", parent=None):
        super().__init__(parent)
        self._text = text
        self._phase = 0.0
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._update)
        self._timer.start(50)

    def _update(self):
        self._phase += 0.1
        if self._phase > 6.28:
            self._phase = 0.0
        self.update()

    def setText(self, text: str):
        self._text = text
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(QColor(C_PURPLE2))
        painter.setFont(self.font())

        import math
        # Simple wave effect on text position
        y_offset = int(math.sin(self._phase) * 5)
        painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter,
                        self._text + f" (phase: {self._phase:.1f})")
