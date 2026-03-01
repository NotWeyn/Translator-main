from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QComboBox, QCheckBox, QPushButton, 
                             QTabWidget, QSpinBox, QApplication)
from PyQt6.QtCore import QTimer, QThread, pyqtSignal
from src.utils.config import ConfigManager
from src.utils.capture import ScreenCapture
from src.core.ocr import EasyOCRBackend
from src.core.text_processor import TextProcessor
from src.core.translator import OpenAITranslator, OfflineTranslator, GoogleTranslator, DeepLTranslator
from src.ui.overlay import OverlayWindow
import sys
import logging
import os
import signal
import time

logger = logging.getLogger(__name__)


class TranslationWorker(QThread):
    """Background worker for continuous translation."""
    translation_complete = pyqtSignal(list)  # Emits translated blocks
    
    def __init__(self, config):
        super().__init__()
        self.config = config
        self.running = False
        self.ocr = None
        self.translator = None
        
    def run(self):
        """Main worker loop."""
        self.running = True
        
        # Initialize OCR
        try:
            use_gpu = self.config.get('use_gpu', True)
            self.ocr = EasyOCRBackend(use_gpu=use_gpu)
        except Exception as e:
            logger.error(f"OCR initialization failed: {e}")
            self.running = False
            return
        
        # Initialize Translator
        try:
            trans_backend = self.config['translator_backend']
            if trans_backend == 'DeepL':
                self.translator = DeepLTranslator(api_key=self.config.get('deepl_api_key'))
            elif trans_backend == 'Google':
                self.translator = GoogleTranslator()
            elif trans_backend == 'OpenAI Compatible LLM':
                self.translator = OpenAITranslator(
                    api_key="dummy", # Local LLMs often don't need a key, or user can provide one if we add a field. For now, dummy.
                    base_url=self.config.get('llm_api_base', 'http://127.0.0.1:5000/v1')
                )
            else:
                self.translator = OfflineTranslator()
        except Exception as e:
            logger.error(f"Translator initialization failed: {e}")
            self.running = False
            return
        
        interval = self.config.get('interval', 5) * 1000  # Convert to milliseconds
        
        while self.running:
            try:
                self.process_translation()
            except Exception as e:
                import traceback
                logger.error(f"Translation error: {e}")
                logger.error(traceback.format_exc())
            
            # Sleep for interval
            self.msleep(interval)
    
    def process_translation(self):
        """Single translation cycle."""
        region = self.config.get('region', '')
        if not region:
            logger.warning("No region selected")
            return
        
        # Capture screenshot
        t_start = time.time()
        temp_image = "/tmp/arch_translator_capture.png"
        if not ScreenCapture.capture_screenshot(temp_image, region):
            logger.error("Capture failed")
            return
        
        # Detect text
        t_ocr_start = time.time()
        raw_results = self.ocr.detect(temp_image)
        if not raw_results:
            logger.info("No text detected")
            return
        
        # Process text
        t_proc_start = time.time()
        processor = TextProcessor()
        merge_dist = self.config.get('merge_distance', 20)
        text_blocks = processor.cluster_text(raw_results, y_threshold=merge_dist)
        
        # Translate
        t_trans_start = time.time()
        
        # Region Checker: If enabled, skip translation and show OCR text directly
        if self.config.get('region_check', False):
            translated_blocks = []
            for block in text_blocks:
                translated_blocks.append({
                    'text': f"{block.text}", # Raw OCR text
                    'bbox': block.bbox
                })
        else:
            target_lang = self.config.get('target_lang', 'tr')
            source_lang = self.config.get('source_lang', 'auto')
            
            translated_blocks = []
            for block in text_blocks:
                translated_text = self.translator.translate(block.text, target_lang, source_lang)
                translated_blocks.append({
                    'text': translated_text,
                    'bbox': block.bbox
                })
        
        # Adjust coordinates for overlay
        try:
            if not region or ' ' not in region:
                logger.warning(f"Invalid region format: '{region}'. Expected 'x,y wxh'.")
                return

            pos_str, size_str = region.split(' ')
            if ',' not in pos_str:
                 logger.warning(f"Invalid position format: '{pos_str}'. Expected 'x,y'.")
                 return
                 
            off_x, off_y = map(int, pos_str.split(','))
            
            final_blocks = []
            for block in translated_blocks:
                new_bbox = []
                for point in block['bbox']:
                    new_bbox.append([point[0] + off_x, point[1] + off_y])
                
                final_blocks.append({
                    'text': block['text'],
                    'bbox': new_bbox
                })
            
            self.translation_complete.emit(final_blocks)
            
            # Performance Logging
            if self.config.get('perf_logging', False):
                t_end = time.time()
                total_time = (t_end - t_start) * 1000
                logger.info(f"[PERF] Total Cycle: {total_time:.2f}ms | "
                            f"Capture: {(t_ocr_start - t_start)*1000:.2f}ms | "
                            f"OCR: {(t_proc_start - t_ocr_start)*1000:.2f}ms | "
                            f"Process: {(t_trans_start - t_proc_start)*1000:.2f}ms | "
                            f"Translate: {(t_end - t_trans_start)*1000:.2f}ms")

        except Exception as e:
            logger.error(f"Error adjusting coordinates: {e}")
    
    def stop(self):
        """Stop the worker."""
        self.running = False


class SettingsWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.config = ConfigManager.load_config()
        self.worker = None
        self.overlay = None
        self.initUI()
        
    def toggle_theme(self):
        """Toggle between dark and light theme."""
        current_theme = self.config.get("theme", "dark")
        new_theme = "light" if current_theme == "dark" else "dark"
        self.config["theme"] = new_theme
        self.auto_save()
        self.apply_theme(new_theme)
        
    def apply_theme(self, theme):
        """Apply stylesheet based on theme."""
        if theme == "dark":
            self.setStyleSheet("""
                QWidget { background-color: #2b2b2b; color: #ffffff; }
                QLineEdit, QComboBox, QSpinBox { background-color: #3b3b3b; color: #ffffff; border: 1px solid #555; }
                QPushButton { background-color: #444; color: #fff; border: 1px solid #555; padding: 5px; }
                QPushButton:hover { background-color: #555; }
                QTabWidget::pane { border: 1px solid #444; }
            """)
        else:
            self.setStyleSheet("") # Reset to default (light)
            
    def initUI(self):
        self.setWindowTitle('Screen Translator')
        self.setGeometry(300, 300, 600, 500)
        
        # Apply initial theme
        self.apply_theme(self.config.get("theme", "dark"))

        layout = QVBoxLayout()
        
        # Tabs
        self.tabs = QTabWidget()
        self.tab_general = QWidget()
        self.tab_ocr = QWidget()
        self.tab_trans = QWidget()
        self.tab_trans = QWidget()
        self.tab_control = QWidget()
        self.tab_dev = QWidget()
        
        self.tabs.addTab(self.tab_control, "Control")
        self.tabs.addTab(self.tab_general, "General")
        self.tabs.addTab(self.tab_ocr, "OCR")
        self.tabs.addTab(self.tab_trans, "Translation")
        self.tabs.addTab(self.tab_dev, "Developer")
        
        self.init_control_tab()
        self.init_general_tab()
        self.init_ocr_tab()
        self.init_trans_tab()
        self.init_dev_tab()
        
        layout.addWidget(self.tabs)
        self.setLayout(layout)

    def init_control_tab(self):
        layout = QVBoxLayout()
        
        # Region Selection
        region_layout = QHBoxLayout()
        region_layout.addWidget(QLabel("Selected Region:"))
        self.region_label = QLabel(self.config.get("region", "None"))
        self.region_label.setWordWrap(True)
        region_layout.addWidget(self.region_label)
        region_layout.addStretch()
        
        select_region_btn = QPushButton("Select Region")
        select_region_btn.clicked.connect(self.select_region)
        region_layout.addWidget(select_region_btn)
        
        layout.addLayout(region_layout)
        
        # Interval
        interval_layout = QHBoxLayout()
        interval_layout.addWidget(QLabel("Check Interval (seconds):"))
        self.interval_spin = QSpinBox()
        self.interval_spin.setMinimum(1)
        self.interval_spin.setMaximum(60)
        self.interval_spin.setValue(self.config.get("interval", 5))
        self.interval_spin.valueChanged.connect(self.auto_save)
        interval_layout.addWidget(self.interval_spin)
        interval_layout.addStretch()
        
        layout.addLayout(interval_layout)
        
        # Hyprland Mode
        self.hyprland_check = QCheckBox("Hyprland Mode (Experimental)")
        self.hyprland_check.setChecked(self.config.get("hyprland_mode", True))
        self.hyprland_check.toggled.connect(self.auto_save)
        layout.addWidget(self.hyprland_check)
        
        # Start/Stop
        control_layout = QHBoxLayout()
        self.start_btn = QPushButton("Start Translation")
        self.start_btn.clicked.connect(self.start_translation)
        control_layout.addWidget(self.start_btn)
        
        self.stop_btn = QPushButton("Stop Translation")
        self.stop_btn.clicked.connect(self.stop_translation)
        self.stop_btn.setEnabled(False)
        control_layout.addWidget(self.stop_btn)
        
        layout.addLayout(control_layout)
        
        # Status
        self.status_label = QLabel("Status: Stopped")
        self.status_label.setStyleSheet("font-weight: bold; color: red;")
        layout.addWidget(self.status_label)
        
        # Theme Toggle (Bottom Right)
        theme_layout = QHBoxLayout()
        theme_layout.addStretch()
        self.theme_btn = QPushButton("Toggle Theme (Dark/Light)")
        self.theme_btn.clicked.connect(self.toggle_theme)
        theme_layout.addWidget(self.theme_btn)
        layout.addLayout(theme_layout)
        
        layout.addStretch()
        self.tab_control.setLayout(layout)

    def init_general_tab(self):
        layout = QVBoxLayout()
        
        # Source Lang
        layout.addWidget(QLabel("Source Language:"))
        self.source_lang_input = QLineEdit(self.config.get("source_lang", "auto"))
        self.source_lang_input.textChanged.connect(self.auto_save)
        layout.addWidget(self.source_lang_input)
        
        # Target Lang
        layout.addWidget(QLabel("Target Language:"))
        self.target_lang_input = QLineEdit(self.config.get("target_lang", "tr"))
        self.target_lang_input.textChanged.connect(self.auto_save)
        layout.addWidget(self.target_lang_input)
        
        layout.addStretch()
        self.tab_general.setLayout(layout)

    def init_ocr_tab(self):
        layout = QVBoxLayout()
        
        # Backend (Removed selection, defaulting to EasyOCR)
        # layout.addWidget(QLabel("OCR Backend:"))
        # self.ocr_backend_combo = QComboBox()
        # self.ocr_backend_combo.addItems(["PaddleOCR", "EasyOCR"])
        # self.ocr_backend_combo.setCurrentText(self.config.get("ocr_backend", "EasyOCR"))
        # self.ocr_backend_combo.currentTextChanged.connect(self.auto_save)
        # layout.addWidget(self.ocr_backend_combo)
        
        # GPU
        self.gpu_check = QCheckBox("Use GPU (Requires CUDA)")
        self.gpu_check.setChecked(self.config.get("use_gpu", True))
        self.gpu_check.toggled.connect(self.auto_save)
        layout.addWidget(self.gpu_check)
        
        # Correction
        self.correction_check = QCheckBox("Enable Text Correction")
        self.correction_check.setChecked(self.config.get("correction_enabled", True))
        self.correction_check.toggled.connect(self.auto_save)
        layout.addWidget(self.correction_check)

        # Merge Distance
        merge_layout = QHBoxLayout()
        merge_layout.addWidget(QLabel("Text Merge Distance (px):"))
        self.merge_spin = QSpinBox()
        self.merge_spin.setMinimum(0)
        self.merge_spin.setMaximum(200)
        self.merge_spin.setValue(self.config.get("merge_distance", 20))
        self.merge_spin.valueChanged.connect(self.auto_save)
        merge_layout.addWidget(self.merge_spin)
        merge_layout.addStretch()
        layout.addLayout(merge_layout)
        
        layout.addStretch()
        self.tab_ocr.setLayout(layout)

    def init_trans_tab(self):
        layout = QVBoxLayout()
        
        # Backend
        layout.addWidget(QLabel("Translation Backend:"))
        self.trans_backend_combo = QComboBox()
        self.trans_backend_combo.addItems(["Argos Translate", "OpenAI Compatible LLM", "Google", "DeepL"])
        self.trans_backend_combo.setCurrentText(self.config.get("translator_backend", "Argos Translate"))
        self.trans_backend_combo.currentTextChanged.connect(self.auto_save)
        self.trans_backend_combo.currentTextChanged.connect(self.update_trans_ui_state)
        layout.addWidget(self.trans_backend_combo)
        
        # OpenAI Key
        # OpenAI Key (Removed as standalone option, but kept in config just in case)
        # self.openai_label = QLabel("OpenAI API Key:")
        # layout.addWidget(self.openai_label)
        # self.openai_key_input = QLineEdit(self.config.get("openai_api_key", ""))
        # self.openai_key_input.setEchoMode(QLineEdit.EchoMode.Password)
        # self.openai_key_input.textChanged.connect(self.auto_save)
        # layout.addWidget(self.openai_key_input)
        
        # DeepL Key
        self.deepl_label = QLabel("DeepL API Key:")
        layout.addWidget(self.deepl_label)
        self.deepl_key_input = QLineEdit(self.config.get("deepl_api_key", ""))
        self.deepl_key_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.deepl_key_input.textChanged.connect(self.auto_save)
        layout.addWidget(self.deepl_key_input)

        # OpenAI Compatible LLM URL
        self.llm_url_label = QLabel("API URL (e.g. http://127.0.0.1:5000/v1):")
        layout.addWidget(self.llm_url_label)
        self.llm_url_input = QLineEdit(self.config.get("llm_api_base", "http://127.0.0.1:5000/v1"))
        self.llm_url_input.textChanged.connect(self.auto_save)
        layout.addWidget(self.llm_url_input)
        
        # Initial UI State Update
        self.update_trans_ui_state(self.trans_backend_combo.currentText())
        
        layout.addStretch()
        self.tab_trans.setLayout(layout)

    def init_dev_tab(self):
        layout = QVBoxLayout()
        
        # Performance Logging
        self.perf_log_check = QCheckBox("Enable Performance Logging (Console)")
        self.perf_log_check.setChecked(self.config.get("perf_logging", False))
        self.perf_log_check.toggled.connect(self.auto_save)
        layout.addWidget(self.perf_log_check)
        
        # Region Checker (OCR Debug)
        self.region_check_box = QCheckBox("Enable Region Checker (Show OCR Text Only)")
        self.region_check_box.setChecked(self.config.get("region_check", False))
        self.region_check_box.toggled.connect(self.auto_save)
        layout.addWidget(self.region_check_box)
        
        layout.addWidget(QLabel("Logs will appear in the terminal where you launched the app."))
        
        layout.addStretch()
        self.tab_dev.setLayout(layout)

    def select_region(self):
        """Select screen region using slurp."""
        region = ScreenCapture.select_region()
        if region:
            self.config['region'] = region
            self.region_label.setText(region)
            self.auto_save()
            logger.info(f"Region selected: {region}")

    def update_trans_ui_state(self, backend):
        """Update visibility of translation settings based on backend."""
        # Hide all first
        self.deepl_label.hide()
        self.deepl_key_input.hide()
        self.llm_url_label.hide()
        self.llm_url_input.hide()
        
        # Show relevant
        # Show relevant
        if backend == "DeepL":
            self.deepl_label.show()
            self.deepl_key_input.show()
        elif backend == "OpenAI Compatible LLM":
            self.llm_url_label.show()
            self.llm_url_input.show()

    def auto_save(self):
        """Auto-save settings whenever changed."""
        new_config = {
            "source_lang": self.source_lang_input.text(),
            "target_lang": self.target_lang_input.text(),
            # "ocr_backend": self.ocr_backend_combo.currentText(), # Removed
            "use_gpu": self.gpu_check.isChecked(),
            "correction_enabled": self.correction_check.isChecked(),
            "merge_distance": self.merge_spin.value(),
            "translator_backend": self.trans_backend_combo.currentText(),
            "deepl_api_key": self.deepl_key_input.text(),
            "llm_api_base": self.llm_url_input.text(),
            "region": self.config.get('region', ''),
            "interval": self.interval_spin.value(),
            "hyprland_mode": self.hyprland_check.isChecked(),
            "perf_logging": self.perf_log_check.isChecked(),
            "region_check": self.region_check_box.isChecked(),
            "theme": self.config.get("theme", "dark")
        }
        
        ConfigManager.save_config(new_config)
        self.config = new_config
        logger.info("Settings auto-saved")

    def start_translation(self):
        """Start the translation worker."""
        if not self.config.get('region'):
            logger.warning("Please select a region first")
            return
        
        # Create overlay
        if not self.overlay:
            hyprland_mode = self.config.get('hyprland_mode', True)
            self.overlay = OverlayWindow(hyprland_mode=hyprland_mode)
        
        # Create and start worker
        self.worker = TranslationWorker(self.config)
        self.worker.translation_complete.connect(self.update_overlay)
        self.worker.start()
        
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.status_label.setText("Status: Running")
        self.status_label.setStyleSheet("font-weight: bold; color: green;")
        logger.info("Translation started")

    def stop_translation(self):
        """Stop the translation worker."""
        if self.worker:
            self.worker.stop()
            self.worker.wait()
            self.worker = None
        
        if self.overlay:
            self.overlay.close()
            self.overlay = None
        
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.status_label.setText("Status: Stopped")
        self.status_label.setStyleSheet("font-weight: bold; color: red;")
        logger.info("Translation stopped")

    def update_overlay(self, blocks):
        """Update overlay with new translated blocks."""
        if self.overlay:
            self.overlay.set_text_blocks(blocks)

    def keyPressEvent(self, event):
        """Handle keyboard shortcuts. ESC to close overlay."""
        from PyQt6.QtCore import Qt
        if event.key() == Qt.Key.Key_Escape:
            if self.overlay:
                self.overlay.close()
                self.overlay = None
                logger.info("Overlay closed via ESC key")
    
    def closeEvent(self, event):
        """Handle window close event."""
        self.stop_translation()
        event.accept()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = SettingsWindow()
    window.show()
    sys.exit(app.exec())
