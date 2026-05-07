"""
engine_v2.py — Improved BGRMeterDetector engine
Matches ZP HIGHER new.exe behavior with production-ready error handling,
proper logging, and accurate shot detection logic from decompiled analysis.
"""

import time
import cv2
import numpy as np
import logging
from typing import Optional, Tuple, List

# BetterCam import with fallback
try:
    from bettercam import BetterCam
    BETTERCAM_OK = True
except ImportError:
    try:
        import bettercam
        BetterCam = bettercam.BetterCam
        BETTERCAM_OK = True
    except ImportError:
        BETTERCAM_OK = False

from core.xinput import read_xinput

logging.basicConfig(
    level=logging.INFO,
    format='[ENGINE] %(asctime)s %(levelname)s: %(message)s',
    datefmt='%H:%M:%S'
)
log = logging.getLogger(__name__)

# BGR ranges from decompiled analysis + exe strings
MAGENTA_FILL_RANGES = [
    (np.array([100, 50, 200]),  np.array([180, 120, 255])),  # pink-magenta
    (np.array([120, 30, 220]),  np.array([200, 100, 255])),  # bright pink
    (np.array([80,  20, 180]),  np.array([160, 90, 255])),   # deep magenta
    (np.array([140, 40, 240]),  np.array([220, 110, 255])),  # light magenta
    (np.array([90,  60, 210]),  np.array([170, 130, 255])),  # mid magenta
]

GREEN_ZONE_RANGES = [
    (np.array([0, 180, 0]),    np.array([80, 255, 80])),    # green
    (np.array([20, 200, 20]),  np.array([100, 255, 100])),  # bright green
    (np.array([0, 160, 0]),    np.array([60, 220, 60])),    # deep green
]

class BGRMeterDetector:
    """Shot meter detector using BGR color ranges (from exe decompilation)."""

    def __init__(self):
        self.calibration_history: List[float] = []
        self.peak_threshold = 0.0
        self.trigger_pct = 0.95  # normal shot
        self.trigger_l2_pct = 0.75  # L2 shot
        self.enabled = True

    def detect_meter(self, frame: np.ndarray) -> Optional[Tuple[float, bool]]:
        """
        Detect shot meter fill percentage and green zone.
        Returns (fill_pct, in_green_zone) or None if no meter found.
        """
        if not self.enabled or frame is None:
            return None

        try:
            # Detect magenta fill
            fill_pct = self._detect_fill(frame)
            if fill_pct is None:
                return None

            # Detect green zone
            in_green = self._detect_green(frame)

            return (fill_pct, in_green)

        except Exception as e:
            log.error(f"Detection error: {e}")
            return None

    def _detect_fill(self, frame: np.ndarray) -> Optional[float]:
        """Detect magenta fill percentage. Returns 0.0-1.0 or None."""
        h, w = frame.shape[:2]
        # Focus on bottom-center region (shot meter location)
        roi = frame[int(h * 0.65):h, int(w * 0.4):int(w * 0.6)]

        if roi.size == 0:
            return None

        # Combine all magenta ranges
        mask = np.zeros(roi.shape[:2], dtype=np.uint8)
        for lower, upper in MAGENTA_FILL_RANGES:
            mask |= cv2.inRange(roi, lower, upper)

        # Find rightmost filled pixel (meter moves left-to-right)
        cols = np.any(mask, axis=0)
        if not np.any(cols):
            return None

        rightmost = np.max(np.where(cols)[0])
        fill_pct = rightmost / roi.shape[1]
        return min(1.0, fill_pct)

    def _detect_green(self, frame: np.ndarray) -> bool:
        """Check if green zone is visible."""
        h, w = frame.shape[:2]
        roi = frame[int(h * 0.65):h, int(w * 0.4):int(w * 0.6)]

        if roi.size == 0:
            return False

        for lower, upper in GREEN_ZONE_RANGES:
            green_mask = cv2.inRange(roi, lower, upper)
            if cv2.countNonZero(green_mask) > 50:  # threshold for green presence
                return True
        return False

    def calibrate(self, fill_pct: float):
        """Update calibration with observed fill percentage."""
        self.calibration_history.append(fill_pct)
        if len(self.calibration_history) > 100:
            self.calibration_history.pop(0)

        # Use 90th percentile as peak threshold (from exe analysis)
        if len(self.calibration_history) >= 10:
            self.peak_threshold = np.percentile(self.calibration_history, 90)


class Engine:
    """Main engine: capture → detect → fire shot."""

    def __init__(self, cam_index: int = 0, fps: int = 240):
        self.detector = BGRMeterDetector()
        self.cam = None
        self.cam_index = cam_index
        self.target_fps = fps
        self.running = False
        self.last_shot_time = 0.0
        self.shot_cooldown = 0.3  # prevent rapid-fire

        if not BETTERCAM_OK:
            log.warning("BetterCam not available — install with: pip install bettercam")

    def start(self):
        """Initialize camera and start capture loop."""
        if not BETTERCAM_OK:
            log.error("Cannot start: BetterCam missing")
            return False

        try:
            self.cam = BetterCam(self.cam_index)
            self.cam.start(region=(0, 0, 1920, 1080), fps=self.target_fps)
            log.info(f"BetterCam started: {self.target_fps} FPS")
        except Exception as e:
            log.error(f"Camera init failed: {e}")
            return False

        self.running = True
        log.info("Engine started")
        return True

    def stop(self):
        self.running = False
        if self.cam:
            try:
                self.cam.stop()
            except:
                pass
        log.info("Engine stopped")

    def run_loop(self, fire_callback=None):
        """
        Main detection loop. Calls fire_callback(fill_pct, in_green) when shot should fire.
        """
        if not self.running:
            log.error("Engine not started")
            return

        frame_time = 1.0 / self.target_fps
        consecutive_misses = 0

        while self.running:
            loop_start = time.perf_counter()

            try:
                frame = self.cam.get_latest_frame()
                if frame is None:
                    consecutive_misses += 1
                    if consecutive_misses > 30:
                        log.warning("30 consecutive missed frames")
                    time.sleep(0.001)
                    continue

                consecutive_misses = 0
                result = self.detector.detect_meter(frame)

                if result:
                    fill_pct, in_green = result
                    self.detector.calibrate(fill_pct)

                    # Fire logic: trigger at 95% fill (normal) or 75% (L2)
                    trigger = self.detector.trigger_pct
                    # TODO: detect L2 state from XInput for trigger_l2_pct
                    if fill_pct >= trigger:
                        now = time.perf_counter()
                        if now - self.last_shot_time > self.shot_cooldown:
                            if fire_callback:
                                fire_callback(fill_pct, in_green)
                            self.last_shot_time = now

            except Exception as e:
                log.error(f"Loop error: {e}")

            # Sleep to maintain FPS
            elapsed = time.perf_counter() - loop_start
            sleep_time = max(0, frame_time - elapsed)
            if sleep_time > 0:
                time.sleep(sleep_time)

    def get_status(self) -> dict:
        return {
            'running': self.running,
            'calibrated': len(self.detector.calibration_history) >= 10,
            'peak_threshold': self.detector.peak_threshold,
            'trigger_pct': self.detector.trigger_pct,
            'bettercam_ok': BETTERCAM_OK,
        }
