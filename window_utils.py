"""
window_utils — Window enumeration for ZP HIGHER
Reconstructed from exe diagnostic output: enumerate_windows, find_remote_play_window
"""

import ctypes
import ctypes.wintypes

user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32

WNDENUMPROC = ctypes.WINFUNCTYPE(
    ctypes.c_bool,
    ctypes.c_void_p,  # HWND
    ctypes.c_void_p   # LPARAM
)


def enumerate_windows() -> list:
    """
    Enumerate all top-level windows.
    Returns list of (hwnd, title, class_name) tuples.
    """
    windows = []

    def enum_callback(hwnd, lparam):
        # Get window title
        length = user32.GetWindowTextLengthW(hwnd)
        if length > 0:
            buffer = ctypes.create_unicode_buffer(length + 1)
            user32.GetWindowTextW(hwnd, buffer, length + 1)
            title = buffer.value
        else:
            title = ""

        # Get class name
        buffer = ctypes.create_unicode_buffer(256)
        user32.GetClassNameW(hwnd, buffer, 256)
        class_name = buffer.value

        windows.append((hwnd, title, class_name))
        return True

    proc = WNDENUMPROC(enum_callback)
    user32.EnumWindows(proc, 0)
    return windows


def find_remote_play_window() -> int or None:
    """
    Find the NBA 2K / Remote Play window.
    Returns HWND if found, None otherwise.
    """
    windows = enumerate_windows()
    keywords = ["nba", "2k", "remote play", "psplay", "chiaki"]

    for hwnd, title, class_name in windows:
        title_lower = title.lower()
        if any(kw in title_lower for kw in keywords):
            return hwnd

    return None


def get_window_rect(hwnd: int) -> dict or None:
    """Get window position and size."""
    rect = ctypes.wintypes.RECT()
    if user32.GetWindowRect(hwnd, ctypes.byref(rect)):
        return {
            'left': rect.left,
            'top': rect.top,
            'right': rect.right,
            'bottom': rect.bottom,
            'width': rect.right - rect.left,
            'height': rect.bottom - rect.top,
        }
    return None
