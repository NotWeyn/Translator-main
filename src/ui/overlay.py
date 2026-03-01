from PyQt6.QtWidgets import QWidget, QApplication, QLabel
from PyQt6.QtGui import QPainter, QColor, QFont, QPen, QBrush, QRegion
from PyQt6.QtCore import Qt, QRect
from typing import List, Dict, Any, Tuple
import sys

class OverlayWindow(QWidget):
    """
    Transparent overlay window to display translated text.
    """
    def __init__(self, hyprland_mode=True):
        super().__init__()
        self.text_blocks = []
        self.hyprland_mode = hyprland_mode
        self.initUI()

    def initUI(self):
        # Window flags for transparency, frameless, and always on top
        if self.hyprland_mode:
            # Hyprland/Wayland mode
            self.setWindowFlags(
                Qt.WindowType.FramelessWindowHint | 
                Qt.WindowType.WindowStaysOnTopHint |
                Qt.WindowType.WindowDoesNotAcceptFocus
            )
            self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)
        else:
            # Classic X11 mode
            self.setWindowFlags(
                Qt.WindowType.FramelessWindowHint | 
                Qt.WindowType.WindowStaysOnTopHint |
                Qt.WindowType.Tool
            )
            # Make the window click-through in non-Hyprland mode
            self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        # Full screen geometry
        screen = QApplication.primaryScreen()
        rect = screen.geometry()
        self.setGeometry(rect)
        
        # Show in fullscreen mode for better Hyprland compatibility
        if self.hyprland_mode:
            self.showFullScreen()
        else:
            # In X11/Non-Hyprland, we also want to cover the screen
            # But we use show() with setGeometry, and sometimes need showMaximized()
            # depending on the WM. Let's try explicit geometry + show.
            self.setGeometry(rect)
            self.show()
            # self.showMaximized() # Alternative if setGeometry fails

    def set_text_blocks(self, blocks: List[Any]):
        """
        Update the text blocks to display.
        Args:
            blocks: List of TextBlock objects or dicts with 'text' and 'bbox'.
        """
        self.text_blocks = blocks
        if self.hyprland_mode:
            self.update_mask()  # Update window shape for Hyprland mode
        self.update()  # Trigger repaint
    def calculate_layout(self) -> List[QRect]:
        """
        Calculate the layout rectangles for all text blocks in Hyprland mode.
        Returns a list of QRect objects representing the background boxes.
        """
        rectangles = []
        
        if not self.hyprland_mode:
            return rectangles
        
        # Create a temporary painter to calculate metrics
        from PyQt6.QtGui import QFontMetrics
        
        for block in self.text_blocks:
            # Handle both dict and object
            if hasattr(block, 'text'):
                text = block.text
                bbox = block.bbox
            else:
                text = block.get('text', '')
                bbox = block.get('bbox', [])

            if not bbox:
                continue

            # bbox is [[x1, y1], [x2, y2], [x3, y3], [x4, y4]]
            x_coords = [p[0] for p in bbox]
            y_coords = [p[1] for p in bbox]
            
            x = min(x_coords)
            y = min(y_coords)
            w = max(x_coords) - x
            h = max(y_coords) - y
            
            # Dynamic Font Scaling & Box Resizing (same logic as paintEvent)
            target_height = h * 0.6
            font_size = max(12, min(int(target_height), 20))
            
            font = QFont("Arial", font_size)
            font.setBold(True)
            metrics = QFontMetrics(font)
            
            # Allow box to expand slightly in width if it's too narrow
            min_width = 100
            draw_w = max(w, min_width)
            
            # Calculate bounding rect for the text with word wrap
            text_rect = metrics.boundingRect(QRect(0, 0, int(draw_w), 0), Qt.TextFlag.TextWordWrap, text)
            
            req_w = text_rect.width()
            req_h = text_rect.height()
            
            # Adjust the background box if the text is larger
            center_x = x + w / 2
            center_y = y + h / 2
            
            final_w = max(w, req_w + 10)  # Add padding
            final_h = max(h, req_h + 10)
            
            final_x = center_x - final_w / 2
            final_y = center_y - final_h / 2
            
            final_rect = QRect(int(final_x), int(final_y), int(final_w), int(final_h))
            rectangles.append(final_rect)
        
        return rectangles

    def update_mask(self):
        """
        Update the window mask to only show the text block regions.
        This makes the empty areas truly transparent and click-through.
        """
        if not self.hyprland_mode:
            return
        
        # Calculate all text block rectangles
        rectangles = self.calculate_layout()
        
        if not rectangles:
            # No text blocks, clear mask (or set to empty region)
            self.clearMask()
            return
        
        # Create a region that combines all rectangles
        region = QRegion()
        for rect in rectangles:
            region = region.united(QRegion(rect))
        
        # Apply the mask to the window
        self.setMask(region)


    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        if not self.hyprland_mode:
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

                
        else:
            # Hyprland/Overlay Mode: Draw text at absolute coordinates
            for block in self.text_blocks:
                # Handle both dict and object (if we use dataclass)
                if hasattr(block, 'text'):
                    text = block.text
                    bbox = block.bbox
                else:
                    text = block.get('text', '')
                    bbox = block.get('bbox', [])
    
                if not bbox:
                    continue
    
                # bbox is [[x1, y1], [x2, y2], [x3, y3], [x4, y4]]
                # We assume a rectangular box for drawing
                x_coords = [p[0] for p in bbox]
                y_coords = [p[1] for p in bbox]
                
                x = min(x_coords)
                y = min(y_coords)
                w = max(x_coords) - x
                h = max(y_coords) - y
                
                # Dynamic Font Scaling & Box Resizing
                # 1. Estimate font size based on box height (initial guess)
                target_height = h * 0.6
                font_size = max(12, min(int(target_height), 20)) # Clamp between 12 and 20
                
                font = QFont("Arial", font_size)
                font.setBold(True)
                painter.setFont(font)
                
                # 2. Calculate required size for text
                metrics = painter.fontMetrics()
                # We want to wrap text, so we constrain width to 'w' (or slightly larger)
                # and see how much height we need.
                
                # Allow box to expand slightly in width if it's too narrow
                min_width = 100
                draw_w = max(w, min_width)
                
                # Calculate bounding rect for the text with word wrap
                text_rect = metrics.boundingRect(QRect(0, 0, int(draw_w), 0), Qt.TextFlag.TextWordWrap, text)
                
                req_w = text_rect.width()
                req_h = text_rect.height()
                
                # 3. Adjust the background box if the text is larger
                # Center the new box on the old box's center
                center_x = x + w / 2
                center_y = y + h / 2
                
                final_w = max(w, req_w + 10) # Add padding
                final_h = max(h, req_h + 10)
                
                final_x = center_x - final_w / 2
                final_y = center_y - final_h / 2
                
                # Draw background box
                bg_color = QColor(0, 0, 0, 160) # Increased opacity for better readability
                painter.setBrush(QBrush(bg_color))
                painter.setPen(Qt.PenStyle.NoPen)
                final_rect = QRect(int(final_x), int(final_y), int(final_w), int(final_h))
                painter.drawRect(final_rect)
                
                # Draw text
                painter.setPen(QColor(255, 255, 0)) # Yellow text
                painter.drawText(final_rect, Qt.AlignmentFlag.AlignCenter | Qt.TextFlag.TextWordWrap, text)
    
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
