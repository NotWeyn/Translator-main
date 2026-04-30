"""
Overlay window — transparent, click-through, always-on-top.

Transparency is achieved via XWayland (xcb platform) with:
  - BypassWindowManagerHint (avoids compositor decoration/compositing issues)
  - WA_TranslucentBackground + WA_NoSystemBackground
  - CompositionMode_Clear in paintEvent to explicitly clear to transparent

Click-through is achieved via X11 XFixes (empty input shape region).
"""

from PyQt6.QtWidgets import QWidget, QApplication
from PyQt6.QtGui import QPainter, QColor, QFont, QPen
from PyQt6.QtCore import Qt, QRect, QTimer
from typing import List, Dict, Any, Optional
import subprocess
import sys
import os
import ctypes
import ctypes.util
import logging

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════════
#  X11 / Compositor helpers
# ═══════════════════════════════════════════════════════════════════════

def _set_x11_click_through(window_id: int) -> bool:
    """Use X11 XFixes to set an empty input shape so all clicks pass through."""
    try:
        x11_path = ctypes.util.find_library("X11")
        xfixes_path = ctypes.util.find_library("Xfixes")
        if not x11_path or not xfixes_path:
            logger.warning("libX11 or libXfixes not found")
            return False

        x11 = ctypes.cdll.LoadLibrary(x11_path)
        xfixes = ctypes.cdll.LoadLibrary(xfixes_path)

        Display_p = ctypes.c_void_p
        Window = ctypes.c_ulong
        XserverRegion = ctypes.c_ulong

        x11.XOpenDisplay.argtypes = [ctypes.c_char_p]
        x11.XOpenDisplay.restype = Display_p
        x11.XFlush.argtypes = [Display_p]
        x11.XFlush.restype = ctypes.c_int
        x11.XCloseDisplay.argtypes = [Display_p]
        x11.XCloseDisplay.restype = ctypes.c_int

        xfixes.XFixesCreateRegion.argtypes = [Display_p, ctypes.c_void_p, ctypes.c_int]
        xfixes.XFixesCreateRegion.restype = XserverRegion
        xfixes.XFixesSetWindowShapeRegion.argtypes = [
            Display_p, Window, ctypes.c_int, ctypes.c_int, ctypes.c_int, XserverRegion
        ]
        xfixes.XFixesSetWindowShapeRegion.restype = None
        xfixes.XFixesDestroyRegion.argtypes = [Display_p, XserverRegion]
        xfixes.XFixesDestroyRegion.restype = None

        display = x11.XOpenDisplay(None)
        if not display:
            logger.warning("Could not open X11 display")
            return False

        empty_region = xfixes.XFixesCreateRegion(display, None, ctypes.c_int(0))
        # ShapeInput = 2
        xfixes.XFixesSetWindowShapeRegion(
            display, Window(window_id), ctypes.c_int(2),
            ctypes.c_int(0), ctypes.c_int(0), empty_region
        )
        xfixes.XFixesDestroyRegion(display, empty_region)
        x11.XFlush(display)
        x11.XCloseDisplay(display)

        logger.info(f"X11 click-through enabled for window 0x{window_id:x}")
        return True
    except Exception as exc:
        logger.error(f"X11 click-through failed: {exc}")
        return False


def _set_hyprland_passthrough(title: str) -> bool:
    """Apply Hyprland window rules as best-effort fallback."""
    try:
        for rule in ["nofocus", "noshadow", "noblur", "pin", "noanim"]:
            subprocess.run(
                ["hyprctl", "keyword", "windowrulev2", f"{rule},title:^({title})$"],
                capture_output=True, timeout=2
            )
        logger.info(f"Hyprland rules applied for '{title}'")
        return True
    except FileNotFoundError:
        return False
    except Exception as exc:
        logger.warning(f"hyprctl failed: {exc}")
        return False


# ═══════════════════════════════════════════════════════════════════════
#  Overlay Window
# ═══════════════════════════════════════════════════════════════════════

class OverlayWindow(QWidget):
    """
    Transparent overlay window to display translated text.

    Supports two rendering modes:
      - **Windowed mode** (overlay_config=None): text shown as a linear list
        inside a dark panel.
      - **Overlay mode** (overlay_config provided): fullscreen transparent
        window; only small boxes behind detected text are semi-opaque.
    """
    OVERLAY_TITLE = "ScreenTranslatorOverlay"

    def __init__(self, overlay_config: Optional[Dict[str, Any]] = None):
        super().__init__()
        self.text_blocks: List[Any] = []
        self.overlay_mode = overlay_config is not None

        if overlay_config:
            self.bg_opacity = overlay_config.get("background_opacity", 0.75)
            self.bg_color = overlay_config.get("background_color", "#000000")
            self.bg_padding = overlay_config.get("background_padding", 4)
            self.font_family = overlay_config.get("font_family", "Arial")
            self.font_size = overlay_config.get("font_size", 14)
            self.font_color = overlay_config.get("font_color", "#FFFFFF")
            self.font_bold = overlay_config.get("font_bold", False)
            self.show_original = overlay_config.get("show_original", False)
            self.click_through = overlay_config.get("click_through", True)
            self.always_on_top = overlay_config.get("always_on_top", True)
        else:
            self.bg_opacity = 0.94
            self.bg_color = "#1e1e1e"
            self.bg_padding = 0
            self.font_family = "Arial"
            self.font_size = 14
            self.font_color = "#FFFFFF"
            self.font_bold = False
            self.show_original = False
            self.click_through = True
            self.always_on_top = True

        self._init_ui()

    # ── Window setup ─────────────────────────────────────────────────

    def _init_ui(self):
        """Configure window flags, attributes, geometry, and show."""

        if self.overlay_mode:
            # Overlay mode: fully transparent, click-through, bypass WM
            flags = (
                Qt.WindowType.FramelessWindowHint
                | Qt.WindowType.WindowStaysOnTopHint
                | Qt.WindowType.BypassWindowManagerHint
            )
            self.setWindowFlags(flags)
            self.setWindowTitle(self.OVERLAY_TITLE)

            # These three attributes together produce a truly transparent
            # window on X11/XWayland:
            self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
            self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground, True)
            self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating, True)

        else:
            # Windowed mode: dark panel, stays on top
            flags = Qt.WindowType.FramelessWindowHint
            if self.always_on_top:
                flags |= Qt.WindowType.WindowStaysOnTopHint
            self.setWindowFlags(flags)
            self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)

        # Fullscreen geometry
        screen = QApplication.primaryScreen()
        rect = screen.geometry()
        self.setGeometry(rect)
        self.show()

        # Apply X11 click-through after the window is mapped
        if self.overlay_mode and self.click_through:
            QTimer.singleShot(500, self._apply_click_through)

    def _apply_click_through(self):
        """Apply OS-level click-through after the window is mapped."""
        platform = QApplication.platformName()
        logger.info(f"Qt platform: {platform}")

        wid = int(self.winId())
        logger.info(f"Window ID: 0x{wid:x}")

        if platform == "xcb":
            if _set_x11_click_through(wid):
                return

        # Fallback: Hyprland rules (nofocus, pin, etc.)
        _set_hyprland_passthrough(self.OVERLAY_TITLE)

    # ── Public API ───────────────────────────────────────────────────

    def set_text_blocks(self, blocks: List[Any]):
        """Update the text blocks to display."""
        self.text_blocks = blocks
        self.update()

    # ── Painting ─────────────────────────────────────────────────────

    def _parse_color(self, hex_color: str, alpha: int = 255) -> QColor:
        color = QColor(hex_color)
        color.setAlpha(alpha)
        return color

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        if self.overlay_mode:
            # Step 1: Clear the entire window to fully transparent.
            # This is CRITICAL — without it, X11 renders black.
            painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_Clear)
            painter.fillRect(self.rect(), Qt.GlobalColor.transparent)

            # Step 2: Switch to normal painting for text boxes.
            painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceOver)
            self._paint_overlay_mode(painter)
        else:
            self._paint_windowed_mode(painter)

        painter.end()

    def _paint_overlay_mode(self, painter: QPainter):
        """Draw translated text over bounding boxes with small background boxes."""
        bg_alpha = int(self.bg_opacity * 255)
        bg_color = self._parse_color(self.bg_color, bg_alpha)
        text_color = self._parse_color(self.font_color)

        font = QFont(self.font_family, self.font_size)
        font.setBold(self.font_bold)
        painter.setFont(font)

        pad = self.bg_padding

        for block in self.text_blocks:
            text = block.get('text', '') if isinstance(block, dict) else getattr(block, 'text', '')
            bbox = block.get('bbox', []) if isinstance(block, dict) else getattr(block, 'bbox', [])
            original = block.get('original', '') if isinstance(block, dict) else ''

            if not bbox or len(bbox) < 4:
                continue

            xs = [p[0] for p in bbox]
            ys = [p[1] for p in bbox]
            x_min, x_max = min(xs), max(xs)
            y_min, y_max = min(ys), max(ys)

            block_rect = QRect(
                int(x_min) - pad, int(y_min) - pad,
                int(x_max - x_min) + 2 * pad, int(y_max - y_min) + 2 * pad
            )

            # Semi-transparent background only behind the text box
            painter.fillRect(block_rect, bg_color)

            if self.show_original and original:
                orig_font = QFont(self.font_family, max(8, self.font_size - 4))
                painter.setFont(orig_font)
                painter.setPen(self._parse_color("#AAAAAA"))
                orig_rect = QRect(block_rect.x(), block_rect.y(),
                                  block_rect.width(), block_rect.height() // 3)
                painter.drawText(orig_rect, Qt.TextFlag.TextWordWrap | Qt.AlignmentFlag.AlignTop, original)
                painter.setFont(font)
                text_rect = QRect(block_rect.x(), block_rect.y() + block_rect.height() // 3,
                                  block_rect.width(), block_rect.height() * 2 // 3)
            else:
                text_rect = block_rect

            painter.setPen(text_color)
            painter.drawText(text_rect, Qt.TextFlag.TextWordWrap | Qt.AlignmentFlag.AlignVCenter, text)

    def _paint_windowed_mode(self, painter: QPainter):
        """Original windowed mode: draw text as a linear list."""
        painter.fillRect(self.rect(), QColor(30, 30, 30, 240))

        y_offset = 20
        padding = 20
        width = self.width() - 2 * padding

        font = QFont("Arial", 14)
        painter.setFont(font)
        painter.setPen(QColor(255, 255, 255))

        for i, block in enumerate(self.text_blocks):
            text = block.get('text', '') if isinstance(block, dict) else getattr(block, 'text', '')

            max_height = self.height() - y_offset - 20
            font_size = 14

            while font_size > 8:
                font = QFont("Arial", font_size)
                painter.setFont(font)
                metrics = painter.fontMetrics()
                rect = metrics.boundingRect(QRect(padding, y_offset, width, max_height),
                                            Qt.TextFlag.TextWordWrap, text)
                if rect.height() <= max_height or font_size == 8:
                    break
                font_size -= 1

            painter.setPen(QColor(255, 255, 255))
            painter.drawText(rect, Qt.TextFlag.TextWordWrap, text)
            y_offset += rect.height() + 10

            if i < len(self.text_blocks) - 1:
                painter.setPen(QPen(QColor(100, 100, 100), 1))
                painter.drawLine(padding, y_offset, self.width() - padding, y_offset)
                y_offset += 15

    # ── Input ────────────────────────────────────────────────────────

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self.close()


if __name__ == '__main__':
    os.environ["QT_QPA_PLATFORM"] = "xcb"

    from PyQt6.QtGui import QSurfaceFormat
    fmt = QSurfaceFormat()
    fmt.setAlphaBufferSize(8)
    QSurfaceFormat.setDefaultFormat(fmt)

    app = QApplication(sys.argv)
    overlay = OverlayWindow(overlay_config={
        "background_opacity": 0.75,
        "background_color": "#000000",
        "background_padding": 6,
        "font_size": 16,
    })
    mock_blocks = [
        {'text': 'Hello World', 'bbox': [[100, 100], [300, 100], [300, 150], [100, 150]]},
        {'text': 'Translation Test', 'bbox': [[400, 200], [600, 200], [600, 250], [400, 250]]},
    ]
    overlay.set_text_blocks(mock_blocks)
    sys.exit(app.exec())
