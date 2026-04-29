from PyQt6.QtWidgets import QWidget, QApplication, QLabel
from PyQt6.QtGui import QPainter, QColor, QFont, QPen, QBrush, QRegion
from PyQt6.QtCore import Qt, QRect
from typing import List, Dict, Any, Tuple, Optional
import sys

class OverlayWindow(QWidget):
    """
    Transparent overlay window to display translated text.
    Supports two rendering modes:
      - Windowed mode (default): text shown as a linear list
      - Overlay mode: text drawn on top of bounding boxes with configurable background
    """
    def __init__(self, overlay_config: Optional[Dict[str, Any]] = None):
        super().__init__()
        self.text_blocks = []
        self.overlay_mode = overlay_config is not None
        
        # Overlay rendering settings (from config.toml [overlay] section)
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
            # Windowed mode defaults
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
        
        self.initUI()

    def initUI(self):
        # Window flags
        flags = Qt.WindowType.FramelessWindowHint | Qt.WindowType.Tool
        if self.always_on_top:
            flags |= Qt.WindowType.WindowStaysOnTopHint
        if self.overlay_mode:
            flags |= Qt.WindowType.X11BypassWindowManagerHint
        self.setWindowFlags(flags)

        # Click-through
        if self.click_through:
            self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)

        # Transparency — all three are needed for true see-through on Wayland
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground, True)
        self.setAutoFillBackground(False)

        # Full screen geometry
        screen = QApplication.primaryScreen()
        rect = screen.geometry()
        self.setGeometry(rect)
        self.show()

    def set_text_blocks(self, blocks: List[Any]):
        """
        Update the text blocks to display.
        Args:
            blocks: List of TextBlock objects or dicts with 'text' and 'bbox'.
                    For overlay mode, may also include 'original' key.
        """
        self.text_blocks = blocks
        self.update()  # Trigger repaint

    def _parse_color(self, hex_color: str, alpha: int = 255) -> QColor:
        """Parse hex color string to QColor with optional alpha."""
        color = QColor(hex_color)
        color.setAlpha(alpha)
        return color

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        if self.overlay_mode:
            # Explicitly clear entire surface to fully transparent
            painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_Clear)
            painter.fillRect(self.rect(), Qt.GlobalColor.transparent)
            painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceOver)
            self._paint_overlay_mode(painter)
        else:
            self._paint_windowed_mode(painter)

    def _paint_overlay_mode(self, painter: QPainter):
        """Draw translated text over bounding boxes with background darkening."""
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
            
            # Calculate bounding rect from bbox points
            xs = [p[0] for p in bbox]
            ys = [p[1] for p in bbox]
            x_min, x_max = min(xs), max(xs)
            y_min, y_max = min(ys), max(ys)
            
            block_rect = QRect(
                int(x_min) - pad,
                int(y_min) - pad,
                int(x_max - x_min) + 2 * pad,
                int(y_max - y_min) + 2 * pad
            )
            
            # Draw background
            painter.fillRect(block_rect, bg_color)
            
            # Draw original text (small, above translated)
            if self.show_original and original:
                orig_font = QFont(self.font_family, max(8, self.font_size - 4))
                painter.setFont(orig_font)
                painter.setPen(self._parse_color("#AAAAAA"))
                orig_rect = QRect(block_rect.x(), block_rect.y(), block_rect.width(), block_rect.height() // 3)
                painter.drawText(orig_rect, Qt.TextFlag.TextWordWrap | Qt.AlignmentFlag.AlignTop, original)
                
                # Reset font for translated text
                painter.setFont(font)
                text_rect = QRect(block_rect.x(), block_rect.y() + block_rect.height() // 3,
                                  block_rect.width(), block_rect.height() * 2 // 3)
            else:
                text_rect = block_rect
            
            # Draw translated text
            painter.setPen(text_color)
            painter.drawText(text_rect, Qt.TextFlag.TextWordWrap | Qt.AlignmentFlag.AlignVCenter, text)

    def _paint_windowed_mode(self, painter: QPainter):
        """Original windowed mode: draw text as a linear list."""
        # Background
        painter.fillRect(self.rect(), QColor(30, 30, 30, 240))
        
        y_offset = 20
        padding = 20
        width = self.width() - 2 * padding
        
        font = QFont("Arial", 14)
        painter.setFont(font)
        painter.setPen(QColor(255, 255, 255))
        
        for i, block in enumerate(self.text_blocks):
            if hasattr(block, 'text'):
                text = block.text
            else:
                text = block.get('text', '')
            
            # Dynamic font sizing for long text
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
            
            # Draw text block
            painter.setPen(QColor(255, 255, 255))
            painter.drawText(rect, Qt.TextFlag.TextWordWrap, text)
            y_offset += rect.height() + 10
            
            # Draw separator line between blocks
            if i < len(self.text_blocks) - 1:
                painter.setPen(QPen(QColor(100, 100, 100), 1))
                painter.drawLine(padding, y_offset, self.width() - padding, y_offset)
                y_offset += 15

    def keyPressEvent(self, event):
        """Handle keyboard shortcuts. ESC to close the overlay."""
        if event.key() == Qt.Key.Key_Escape:
            self.close()

if __name__ == '__main__':
    # Test
    app = QApplication(sys.argv)
    overlay = OverlayWindow()
    
    # Mock data
    mock_blocks = [
        {'text': 'Hello World', 'bbox': [[100, 100], [300, 100], [300, 150], [100, 150]]},
        {'text': 'Translation Test', 'bbox': [[400, 200], [600, 200], [600, 250], [400, 250]]}
    ]
    overlay.set_text_blocks(mock_blocks)
    
    sys.exit(app.exec())
