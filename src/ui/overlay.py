from PyQt6.QtWidgets import QWidget, QApplication, QLabel
from PyQt6.QtGui import QPainter, QColor, QFont, QPen, QBrush, QRegion
from PyQt6.QtCore import Qt, QRect
from typing import List, Dict, Any, Tuple
import sys

class OverlayWindow(QWidget):
    """
    Transparent overlay window to display translated text.
    """
    def __init__(self):
        super().__init__()
        self.text_blocks = []
        self.initUI()

    def initUI(self):
        # Window flags for transparency, frameless, and always on top
        # Classic X11 / Windowed mode
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint | 
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        # Make the window click-through
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

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
        """
        self.text_blocks = blocks
        self.update()  # Trigger repaint

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Windowed Mode: Draw text linearly as a list
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
            # Start with default size and reduce if text doesn't fit
            max_height = self.height() - y_offset - 20  # Reserve space
            font_size = 14
            
            while font_size > 8:  # Minimum font size
                font = QFont("Arial", font_size)
                painter.setFont(font)
                metrics = painter.fontMetrics()
                rect = metrics.boundingRect(QRect(padding, y_offset, width, max_height), 
                                            Qt.TextFlag.TextWordWrap, text)
                
                # If text fits within available space, use this font size
                if rect.height() <= max_height or font_size == 8:
                    break
                font_size -= 1
            
            # Draw text block
            painter.setPen(QColor(255, 255, 255))
            painter.drawText(rect, Qt.TextFlag.TextWordWrap, text)
            y_offset += rect.height() + 10  # Add spacing
            
            # Draw separator line between blocks (except after last block)
            if i < len(self.text_blocks) - 1:
                painter.setPen(QPen(QColor(100, 100, 100), 1))
                painter.drawLine(padding, y_offset, self.width() - padding, y_offset)
                y_offset += 15  # Space after separator

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
