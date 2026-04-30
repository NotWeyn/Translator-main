"""
Headless overlay application — launched via ``./start.sh --overlay``.

Runs without the Settings GUI.  All configuration is read from ``config.toml``.
Creates a fullscreen, click-through overlay and continuously captures → OCR →
translates → renders on screen.
"""

import sys
import os
import signal
import logging
import time

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer, QThread, pyqtSignal
from PyQt6.QtGui import QSurfaceFormat

from src.utils.config import ConfigManager
from src.utils.capture import ScreenCapture
from src.core.ocr import EasyOCRBackend, PaddleOCRBackend
from src.core.text_processor import TextProcessor
from src.core.translator import (
    OpenAITranslator, OfflineTranslator, GoogleTranslator, DeepLTranslator
)
from src.ui.overlay import OverlayWindow

logger = logging.getLogger(__name__)


class OverlayWorker(QThread):
    """Background translation loop for overlay mode."""
    translation_complete = pyqtSignal(list)
    error_occurred = pyqtSignal(str)

    def __init__(self, config):
        super().__init__()
        self.config = config
        self.running = False

    def run(self):
        self.running = True

        # ── OCR init ──
        try:
            use_gpu = self.config["ocr"]["use_gpu"]
            backend = self.config["ocr"]["backend"]
            if backend == "PaddleOCR":
                self.ocr = PaddleOCRBackend(use_gpu=use_gpu)
            else:
                self.ocr = EasyOCRBackend(use_gpu=use_gpu)
        except Exception as exc:
            self.error_occurred.emit(f"OCR init failed: {exc}")
            self.running = False
            return

        # ── Translator init ──
        try:
            tb = self.config["translation"]["backend"]
            if tb == "DeepL":
                self.translator = DeepLTranslator(
                    api_key=self.config["translation"]["deepl_api_key"]
                )
            elif tb == "Google":
                self.translator = GoogleTranslator()
            elif tb == "OpenAI Compatible LLM":
                self.translator = OpenAITranslator(
                    api_key="dummy",
                    base_url=self.config["translation"]["llm_api_base"],
                )
            else:
                self.translator = OfflineTranslator()
        except Exception as exc:
            self.error_occurred.emit(f"Translator init failed: {exc}")
            self.running = False
            return

        # Use overlay-specific refresh interval, fall back to capture interval
        interval_sec = self.config["overlay"].get(
            "refresh_interval",
            self.config["capture"]["interval"],
        )
        interval_ms = int(interval_sec * 1000)

        while self.running:
            try:
                self._cycle()
            except Exception as exc:
                import traceback
                logger.error(f"Overlay cycle error: {exc}")
                logger.error(traceback.format_exc())
            self.msleep(interval_ms)

    # ── single capture-translate cycle ──────────────────────────────

    def _cycle(self):
        # Determine region: overlay.target_region overrides capture.region
        region = (
            self.config["overlay"].get("target_region")
            or self.config["capture"]["region"]
        )
        if not region:
            logger.warning("No region configured (capture.region / overlay.target_region)")
            return

        t0 = time.time()
        temp_img = "/tmp/screen_translator_overlay.png"
        if not ScreenCapture.capture_screenshot(temp_img, region):
            return

        t1 = time.time()
        raw = self.ocr.detect(temp_img)
        if not raw:
            # Clear overlay when no text detected
            self.translation_complete.emit([])
            return

        t2 = time.time()
        processor = TextProcessor()
        merge_dist = self.config["ocr"]["merge_distance"]
        blocks = processor.cluster_text(raw, y_threshold=merge_dist)

        t3 = time.time()

        # Region checker (developer debug)
        if self.config["developer"]["region_check"]:
            result = [{"text": b.text, "bbox": b.bbox, "original": b.text} for b in blocks]
        else:
            target = self.config["general"]["target_lang"]
            source = self.config["general"]["source_lang"]
            result = []
            for b in blocks:
                translated = self.translator.translate(b.text, target, source)
                result.append({
                    "text": translated,
                    "bbox": b.bbox,
                    "original": b.text,
                })

        # Offset bbox by region origin
        try:
            if " " not in region or "," not in region.split(" ")[0]:
                logger.warning(f"Invalid region format: '{region}'")
                return
            pos, _ = region.split(" ")
            off_x, off_y = map(int, pos.split(","))
            for item in result:
                item["bbox"] = [[p[0] + off_x, p[1] + off_y] for p in item["bbox"]]
        except Exception as exc:
            logger.error(f"Coordinate adjustment error: {exc}")
            return

        self.translation_complete.emit(result)

        if self.config["developer"]["perf_logging"]:
            t4 = time.time()
            logger.info(
                f"[PERF-OVERLAY] Total: {(t4-t0)*1000:.0f}ms | "
                f"Cap: {(t1-t0)*1000:.0f}ms | OCR: {(t2-t1)*1000:.0f}ms | "
                f"Proc: {(t3-t2)*1000:.0f}ms | Trans: {(t4-t3)*1000:.0f}ms"
            )

    def stop(self):
        self.running = False


def run_overlay():
    """Entry point for ``--overlay`` mode."""
    config = ConfigManager.load_config()

    # Configure log level from config
    log_level = config["developer"].get("log_level", "INFO").upper()
    logging.basicConfig(level=getattr(logging, log_level, logging.INFO),
                        format="%(levelname)s:%(name)s:%(message)s")

    # ── Force XCB (XWayland) for transparent overlay ──
    # WA_TranslucentBackground does NOT work on native Wayland — compositors
    # render the surface as opaque black.  Running under XWayland (xcb) is the
    # standard workaround used by overlay-type apps on Linux.  This works on
    # KDE Plasma, Gamescope, Hyprland, and any compositor with XWayland.
    os.environ["QT_QPA_PLATFORM"] = "xcb"
    logger.info("Overlay mode: forcing xcb (XWayland) for transparency support")

    # Ensure the surface format has an alpha channel
    fmt = QSurfaceFormat()
    fmt.setAlphaBufferSize(8)
    QSurfaceFormat.setDefaultFormat(fmt)

    app = QApplication(sys.argv)

    # Create overlay window with config
    overlay = OverlayWindow(overlay_config=config["overlay"])

    # Create & start worker
    worker = OverlayWorker(config)
    worker.translation_complete.connect(overlay.set_text_blocks)
    worker.error_occurred.connect(lambda msg: logger.error(msg))
    worker.start()

    # Graceful shutdown
    def shutdown(*_):
        logger.info("Shutting down overlay…")
        worker.stop()
        worker.wait()
        overlay.close()
        app.quit()

    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)

    # Timer so Python signal handlers can fire
    tick = QTimer()
    tick.start(500)
    tick.timeout.connect(lambda: None)

    logger.info("Overlay mode started — press Ctrl+C or ESC to exit")
    sys.exit(app.exec())
