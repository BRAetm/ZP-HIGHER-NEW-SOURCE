"""
security.py — Process integrity checks and periodic auth.
Reconstructed from exe diagnostic output (diag2.txt)
SEC_CLASS PeriodicAuthChecker: start,stop
SECURITY_ATTRS=PeriodicAuthChecker,ctypes,hashlib,os,run_security_checks,start_background_monitor,...
"""
import ctypes
import os
import threading
import time
import hashlib
import struct
import subprocess
import sys

import psutil


class Security:
    BLOCKED_PROCESSES = [
        "cheatengine", "ollydbg", "x64dbg", "x32dbg",
        "ida", "ida64", "idat", "idat64",
        "wireshark", "fiddler", "procmon", "processhacker",
        "httpdebugger", "charles",
    ]

    def verify(self) -> bool:
        if self._debugger_present():
            return False
        if self._analysis_tools_running():
            return False
        return True

    def _debugger_present(self) -> bool:
        try:
            return bool(ctypes.windll.kernel32.IsDebuggerPresent())
        except Exception:
            return False

    def _analysis_tools_running(self) -> bool:
        try:
            for proc in psutil.process_iter(["name"]):
                name = (proc.info["name"] or "").lower()
                if any(b in name for b in self.BLOCKED_PROCESSES):
                    return True
        except Exception:
            pass
        return False


class PeriodicAuthChecker:
    """Periodic KeyAuth validation (from diag2.txt: start,stop methods)."""

    def __init__(self, interval: int = 300):
        self.interval = interval  # seconds
        self._running = False
        self._thread = None

    def start(self):
        """Start periodic auth checking."""
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._check_loop, daemon=True)
        self._thread.start()

    def stop(self):
        """Stop periodic auth checking."""
        self._running = False
        if self._thread:
            self._thread.join(timeout=5)

    def _check_loop(self):
        """Background loop that validates auth periodically."""
        while self._running:
            try:
                run_security_checks()
            except Exception:
                pass
            time.sleep(self.interval)


def run_security_checks():
    """Run all security checks (from diag2.txt)."""
    sec = Security()
    if not sec.verify():
        sys.exit(1)


def start_background_monitor():
    """Start background security monitor (from diag2.txt)."""
    checker = PeriodicAuthChecker()
    checker.start()
    return checker
