"""
LoginPage — KeyAuth login widget for ZP HIGHER
Reconstructed from exe diagnostic output
CLASS LoginPage: PaintDeviceMetric,RenderFlag,acceptDrops,...
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QMessageBox
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QColor

from keyauth import KeyAuthApp
from security import PeriodicAuthChecker

C_BG = "#1a1a2e"
C_BLUE2 = "#0f3460"
C_BORDER_PURPLE = "#7b2d8e"
C_PURPLE2 = "#a29bfe"
C_TEXT = "#e0e0e0"
C_ERROR = "#ff4757"
C_SUCCESS = "#00d2d3"


class LoginPage(QWidget):
    """KeyAuth login page with license key validation."""

    login_success = Signal()
    login_failed = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.keyauth = KeyAuthApp()
        self.auth_checker = PeriodicAuthChecker()
        self._setup_ui()

    def _setup_ui(self):
        self.setStyleSheet(f"background-color: {C_BG};")

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(20)

        # Title
        title = QLabel("ZP HIGHER Login")
        title.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {C_PURPLE2};")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # Subtitle
        sub = QLabel("Enter your license key to continue")
        sub.setFont(QFont("Arial", 12))
        sub.setStyleSheet(f"color: {C_TEXT};")
        sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(sub)

        layout.addSpacing(20)

        # Key input
        input_layout = QHBoxLayout()

        self.txt_key = QLineEdit()
        self.txt_key.setPlaceholderText("License Key...")
        self.txt_key.setFixedWidth(300)
        self.txt_key.setStyleSheet(f"""
            QLineEdit {{
                background-color: {C_BLUE2};
                border: 1px solid {C_BORDER_PURPLE};
                border-radius: 6px;
                padding: 8px;
                color: {C_TEXT};
                font-size: 14px;
            }}
        """)

        btn_login = QPushButton("Login")
        btn_login.setFixedWidth(100)
        btn_login.setStyleSheet(f"""
            QPushButton {{
                background-color: {C_BORDER_PURPLE};
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {C_PURPLE2};
            }}
        """)
        btn_login.clicked.connect(self._attempt_login)

        input_layout.addStretch()
        input_layout.addWidget(self.txt_key)
        input_layout.addWidget(btn_login)
        input_layout.addStretch()

        layout.addLayout(input_layout)

        # Status label
        self.lbl_status = QLabel("")
        self.lbl_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_status.setStyleSheet(f"color: {C_TEXT2};")
        layout.addWidget(self.lbl_status)

        layout.addStretch()

    def _attempt_login(self):
        """Attempt KeyAuth login."""
        key = self.txt_key.text().strip()
        if not key:
            self.lbl_status.setStyleSheet(f"color: {C_ERROR};")
            self.lbl_status.setText("Please enter a license key")
            return

        self.lbl_status.setStyleSheet(f"color: {C_TEXT2};")
        self.lbl_status.setText("Validating...")

        # TODO: Actual KeyAuth validation
        # For now, simulate success
        if len(key) > 10:
            self.lbl_status.setStyleSheet(f"color: {C_SUCCESS};")
            self.lbl_status.setText("Login successful!")
            self.login_success.emit()
        else:
            self.lbl_status.setStyleSheet(f"color: {C_ERROR};")
            self.lbl_status.setText("Invalid license key")
            self.login_failed.emit("Invalid key")

    def start_auth_checker(self):
        """Start periodic auth checking."""
        self.auth_checker.start()
