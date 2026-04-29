from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QLineEdit, QComboBox, QCheckBox, QPushButton,
                             QSpinBox, QApplication, QSizePolicy, QFrame,
                             QStackedWidget, QScrollArea, QGraphicsDropShadowEffect)
from PyQt6.QtCore import QTimer, QThread, pyqtSignal, Qt, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QColor, QFont
from src.utils.config import ConfigManager
from src.utils.capture import ScreenCapture
from src.core.ocr import EasyOCRBackend, PaddleOCRBackend
from src.core.text_processor import TextProcessor
from src.core.translator import OpenAITranslator, OfflineTranslator, GoogleTranslator, DeepLTranslator
from src.ui.overlay import OverlayWindow
from src.ui.theme import build_stylesheet
import sys
import logging
import os
import signal
import time

logger = logging.getLogger(__name__)


class TranslationWorker(QThread):
    """Background worker for continuous translation."""
    translation_complete = pyqtSignal(list)
    error_occurred = pyqtSignal(str)

    def __init__(self, config):
        super().__init__()
        self.config = config
        self.running = False
        self.ocr = None
        self.translator = None

    def run(self):
        """Main worker loop."""
        self.running = True
        try:
            use_gpu = self.config["ocr"]["use_gpu"]
            ocr_backend = self.config["ocr"]["backend"]
            if ocr_backend == 'PaddleOCR':
                self.ocr = PaddleOCRBackend(use_gpu=use_gpu)
            else:
                self.ocr = EasyOCRBackend(use_gpu=use_gpu)
        except Exception as e:
            logger.error(f"OCR initialization failed: {e}")
            self.error_occurred.emit(str(e))
            self.running = False
            return

        try:
            trans_backend = self.config["translation"]["backend"]
            if trans_backend == 'DeepL':
                self.translator = DeepLTranslator(api_key=self.config["translation"]["deepl_api_key"])
            elif trans_backend == 'Google':
                self.translator = GoogleTranslator()
            elif trans_backend == 'OpenAI Compatible LLM':
                self.translator = OpenAITranslator(
                    api_key="dummy",
                    base_url=self.config["translation"]["llm_api_base"]
                )
            else:
                self.translator = OfflineTranslator()
        except Exception as e:
            logger.error(f"Translator initialization failed: {e}")
            self.running = False
            return

        interval = self.config["capture"]["interval"] * 1000
        while self.running:
            try:
                self.process_translation()
            except Exception as e:
                import traceback
                logger.error(f"Translation error: {e}")
                logger.error(traceback.format_exc())
            self.msleep(interval)

    def process_translation(self):
        """Single translation cycle."""
        region = self.config["capture"]["region"]
        if not region:
            logger.warning("No region selected")
            return

        t_start = time.time()
        temp_image = "/tmp/screen_translator_capture.png"
        if not ScreenCapture.capture_screenshot(temp_image, region):
            logger.error("Capture failed")
            return

        t_ocr_start = time.time()
        raw_results = self.ocr.detect(temp_image)
        if not raw_results:
            logger.info("No text detected")
            return

        t_proc_start = time.time()
        processor = TextProcessor()
        merge_dist = self.config["ocr"]["merge_distance"]
        text_blocks = processor.cluster_text(raw_results, y_threshold=merge_dist)

        t_trans_start = time.time()
        if self.config["developer"]["region_check"]:
            translated_blocks = [{'text': block.text, 'bbox': block.bbox} for block in text_blocks]
        else:
            target_lang = self.config["general"]["target_lang"]
            source_lang = self.config["general"]["source_lang"]
            translated_blocks = []
            for block in text_blocks:
                translated_text = self.translator.translate(block.text, target_lang, source_lang)
                translated_blocks.append({'text': translated_text, 'bbox': block.bbox})

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
                new_bbox = [[p[0] + off_x, p[1] + off_y] for p in block['bbox']]
                final_blocks.append({'text': block['text'], 'bbox': new_bbox})
            self.translation_complete.emit(final_blocks)

            if self.config["developer"]["perf_logging"]:
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
        self.running = False


# ─── UI Helper Functions ─────────────────────────────────────────────

def _make_card(title=None, description=None):
    """Create a styled card QFrame."""
    card = QFrame()
    card.setProperty("class", "card")
    card_layout = QVBoxLayout(card)
    card_layout.setContentsMargins(20, 16, 20, 16)
    card_layout.setSpacing(12)

    if title:
        t = QLabel(title)
        t.setProperty("class", "card-title")
        card_layout.addWidget(t)
    if description:
        d = QLabel(description)
        d.setProperty("class", "card-desc")
        d.setWordWrap(True)
        card_layout.addWidget(d)

    shadow = QGraphicsDropShadowEffect()
    shadow.setBlurRadius(20)
    shadow.setOffset(0, 2)
    shadow.setColor(QColor(0, 0, 0, 30))
    card.setGraphicsEffect(shadow)
    return card, card_layout


def _make_field_label(text):
    lbl = QLabel(text)
    lbl.setProperty("class", "field-label")
    return lbl


def _make_btn(text, cls="btn-primary"):
    btn = QPushButton(text)
    btn.setProperty("class", cls)
    btn.setCursor(Qt.CursorShape.PointingHandCursor)
    return btn


def _h_field(label_text, widget, stretch=True):
    """Horizontal label + widget row."""
    row = QHBoxLayout()
    row.addWidget(_make_field_label(label_text))
    row.addWidget(widget)
    if stretch:
        row.addStretch()
    return row


# ─── Main Window ─────────────────────────────────────────────────────

NAV_ITEMS = [
    ("⚡", "Control"),
    ("🌐", "General"),
    ("👁", "OCR"),
    ("🔄", "Translation"),
    ("🛠", "Developer"),
]


class SettingsWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.config = ConfigManager.load_config()
        self.worker = None
        self.overlay = None
        self.nav_buttons = []
        self.current_nav = 0
        self.initUI()

    # ── Theme ────────────────────────────────────────────────────────

    def toggle_theme(self):
        current = self.config["general"]["theme"]
        new_theme = "light" if current == "dark" else "dark"
        self.config["general"]["theme"] = new_theme
        self.auto_save()
        self.apply_theme(new_theme)

    def apply_theme(self, theme):
        self.setStyleSheet(build_stylesheet(theme))
        icon = "☀️" if theme == "dark" else "🌙"
        label = "Light Mode" if theme == "dark" else "Dark Mode"
        if hasattr(self, 'theme_btn'):
            self.theme_btn.setText(f"{icon}  {label}")

    # ── UI Init ──────────────────────────────────────────────────────

    def initUI(self):
        self.setObjectName("CentralWidget")
        self.setWindowTitle('Screen Translator')
        self.setMinimumSize(820, 540)
        self.resize(820, 540)

        root = QHBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── Sidebar ──
        sidebar = QFrame()
        sidebar.setObjectName("Sidebar")
        sidebar.setFixedWidth(220)
        sb_layout = QVBoxLayout(sidebar)
        sb_layout.setContentsMargins(14, 20, 14, 16)
        sb_layout.setSpacing(4)

        # App branding
        title = QLabel("Screen Translator")
        title.setObjectName("AppTitle")
        sb_layout.addWidget(title)
        subtitle = QLabel("Real-time OCR & Translation")
        subtitle.setObjectName("AppSubtitle")
        sb_layout.addWidget(subtitle)
        sb_layout.addSpacing(20)

        # Nav items
        for i, (icon, label) in enumerate(NAV_ITEMS):
            btn = QPushButton(f"  {icon}   {label}")
            btn.setProperty("class", "nav-item")
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setFixedHeight(40)
            btn.clicked.connect(lambda checked, idx=i: self._nav_click(idx))
            sb_layout.addWidget(btn)
            self.nav_buttons.append(btn)

        sb_layout.addStretch()

        # Theme toggle at bottom
        self.theme_btn = QPushButton()
        self.theme_btn.setObjectName("ThemeToggle")
        self.theme_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.theme_btn.clicked.connect(self.toggle_theme)
        sb_layout.addWidget(self.theme_btn)

        root.addWidget(sidebar)

        # ── Content Area ──
        self.stacked = QStackedWidget()
        self.stacked.setContentsMargins(0, 0, 0, 0)

        self._build_control_page()
        self._build_general_page()
        self._build_ocr_page()
        self._build_trans_page()
        self._build_dev_page()

        root.addWidget(self.stacked, 1)

        # Apply theme & set initial nav
        self.apply_theme(self.config["general"]["theme"])
        self._nav_click(0)

    def _nav_click(self, idx):
        self.current_nav = idx
        self.stacked.setCurrentIndex(idx)
        for i, btn in enumerate(self.nav_buttons):
            btn.setProperty("class", "nav-active" if i == idx else "nav-item")
            btn.style().unpolish(btn)
            btn.style().polish(btn)

    # ── Page Builder Helper ──────────────────────────────────────────

    def _make_page(self, title, desc):
        """Create a scrollable page with header."""
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(32, 28, 32, 28)
        layout.setSpacing(16)

        t = QLabel(title)
        t.setObjectName("PageTitle")
        layout.addWidget(t)

        d = QLabel(desc)
        d.setObjectName("PageDesc")
        d.setWordWrap(True)
        layout.addWidget(d)
        layout.addSpacing(4)

        scroll.setWidget(container)
        self.stacked.addWidget(scroll)
        return layout

    # ── Control Page ─────────────────────────────────────────────────

    def _build_control_page(self):
        page = self._make_page("Control Panel", "Manage translation capture and monitor status.")

        # Status Card
        card, cl = _make_card("Status")
        self.status_dot = QLabel("●")
        self.status_dot.setFixedWidth(20)
        self.status_text = QLabel("Stopped")
        self.status_text.setObjectName("StatusStopped")
        row = QHBoxLayout()
        row.addWidget(self.status_dot)
        row.addWidget(self.status_text)
        row.addStretch()
        cl.addLayout(row)
        page.addWidget(card)

        # Region Card
        card, cl = _make_card("Capture Region", "Select screen area to capture and translate.")
        self.region_label = QLabel(self.config["capture"]["region"] or "No region selected")
        self.region_label.setObjectName("RegionValue")
        self.region_label.setWordWrap(True)
        cl.addWidget(self.region_label)
        select_btn = _make_btn("📐  Select Region", "btn-secondary")
        select_btn.clicked.connect(self.select_region)
        cl.addWidget(select_btn)
        page.addWidget(card)

        # Interval Card
        card, cl = _make_card("Capture Interval")
        self.interval_spin = QSpinBox()
        self.interval_spin.setMinimum(1)
        self.interval_spin.setMaximum(60)
        self.interval_spin.setValue(self.config["capture"]["interval"])
        self.interval_spin.setSuffix("  seconds")
        self.interval_spin.setFixedWidth(160)
        self.interval_spin.valueChanged.connect(self.auto_save)
        cl.addLayout(_h_field("Interval", self.interval_spin))
        page.addWidget(card)

        # Action Buttons
        card, cl = _make_card()
        btn_row = QHBoxLayout()
        self.start_btn = _make_btn("▶  Start Translation", "btn-primary")
        self.start_btn.clicked.connect(self.start_translation)
        btn_row.addWidget(self.start_btn)
        self.stop_btn = _make_btn("■  Stop", "btn-danger")
        self.stop_btn.clicked.connect(self.stop_translation)
        self.stop_btn.setEnabled(False)
        btn_row.addWidget(self.stop_btn)
        btn_row.addStretch()
        cl.addLayout(btn_row)
        page.addWidget(card)

        page.addStretch()
        self._update_status_display(False)

    # ── General Page ─────────────────────────────────────────────────

    def _build_general_page(self):
        page = self._make_page("General", "Language and basic preferences.")

        card, cl = _make_card("Languages", "Configure source and target languages for translation.")
        cl.addWidget(_make_field_label("Source Language"))
        self.source_lang_input = QLineEdit(self.config["general"]["source_lang"])
        self.source_lang_input.setPlaceholderText("auto")
        self.source_lang_input.textChanged.connect(self.auto_save)
        cl.addWidget(self.source_lang_input)

        cl.addSpacing(4)
        cl.addWidget(_make_field_label("Target Language"))
        self.target_lang_input = QLineEdit(self.config["general"]["target_lang"])
        self.target_lang_input.setPlaceholderText("tr")
        self.target_lang_input.textChanged.connect(self.auto_save)
        cl.addWidget(self.target_lang_input)
        page.addWidget(card)

        page.addStretch()

    # ── OCR Page ─────────────────────────────────────────────────────

    def _build_ocr_page(self):
        page = self._make_page("OCR Settings", "Optical character recognition engine configuration.")

        card, cl = _make_card("Engine")
        cl.addWidget(_make_field_label("OCR Backend"))
        self.ocr_backend_combo = QComboBox()
        self.ocr_backend_combo.addItems(["EasyOCR", "PaddleOCR"])
        self.ocr_backend_combo.setCurrentText(self.config["ocr"]["backend"])
        self.ocr_backend_combo.currentTextChanged.connect(self.auto_save)
        cl.addWidget(self.ocr_backend_combo)

        cl.addSpacing(8)
        self.gpu_check = QCheckBox("Use GPU acceleration (CUDA)")
        self.gpu_check.setChecked(self.config["ocr"]["use_gpu"])
        self.gpu_check.toggled.connect(self.auto_save)
        cl.addWidget(self.gpu_check)
        page.addWidget(card)

        card, cl = _make_card("Processing")
        self.correction_check = QCheckBox("Enable text correction")
        self.correction_check.setChecked(self.config["ocr"]["correction_enabled"])
        self.correction_check.toggled.connect(self.auto_save)
        cl.addWidget(self.correction_check)

        cl.addSpacing(4)
        self.merge_spin = QSpinBox()
        self.merge_spin.setMinimum(0)
        self.merge_spin.setMaximum(200)
        self.merge_spin.setValue(self.config["ocr"]["merge_distance"])
        self.merge_spin.setSuffix("  px")
        self.merge_spin.setFixedWidth(140)
        self.merge_spin.valueChanged.connect(self.auto_save)
        cl.addLayout(_h_field("Text merge distance", self.merge_spin))
        page.addWidget(card)

        page.addStretch()

    # ── Translation Page ─────────────────────────────────────────────

    def _build_trans_page(self):
        page = self._make_page("Translation", "Choose translation engine and configure API keys.")

        card, cl = _make_card("Engine")
        cl.addWidget(_make_field_label("Translation Backend"))
        self.trans_backend_combo = QComboBox()
        self.trans_backend_combo.addItems(["Argos Translate", "OpenAI Compatible LLM", "Google", "DeepL"])
        self.trans_backend_combo.setCurrentText(self.config["translation"]["backend"])
        self.trans_backend_combo.currentTextChanged.connect(self.auto_save)
        self.trans_backend_combo.currentTextChanged.connect(self.update_trans_ui_state)
        cl.addWidget(self.trans_backend_combo)
        page.addWidget(card)

        # DeepL card
        self.deepl_card, cl = _make_card("DeepL Configuration")
        cl.addWidget(_make_field_label("API Key"))
        self.deepl_key_input = QLineEdit(self.config["translation"]["deepl_api_key"])
        self.deepl_key_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.deepl_key_input.setPlaceholderText("Enter your DeepL API key")
        self.deepl_key_input.textChanged.connect(self.auto_save)
        cl.addWidget(self.deepl_key_input)
        page.addWidget(self.deepl_card)

        # LLM card
        self.llm_card, cl = _make_card("LLM Configuration")
        cl.addWidget(_make_field_label("API URL"))
        self.llm_url_input = QLineEdit(self.config["translation"]["llm_api_base"])
        self.llm_url_input.setPlaceholderText("http://127.0.0.1:5000/v1")
        self.llm_url_input.textChanged.connect(self.auto_save)
        cl.addWidget(self.llm_url_input)
        page.addWidget(self.llm_card)

        self.update_trans_ui_state(self.trans_backend_combo.currentText())
        page.addStretch()

    # ── Developer Page ───────────────────────────────────────────────

    def _build_dev_page(self):
        page = self._make_page("Developer", "Debugging and performance tools.")

        card, cl = _make_card("Debug Tools")
        self.perf_log_check = QCheckBox("Enable performance logging (console)")
        self.perf_log_check.setChecked(self.config["developer"]["perf_logging"])
        self.perf_log_check.toggled.connect(self.auto_save)
        cl.addWidget(self.perf_log_check)

        cl.addSpacing(4)
        self.region_check_box = QCheckBox("Region checker (show raw OCR output)")
        self.region_check_box.setChecked(self.config["developer"]["region_check"])
        self.region_check_box.toggled.connect(self.auto_save)
        cl.addWidget(self.region_check_box)

        cl.addSpacing(8)
        hint = QLabel("Logs appear in the terminal where the app was launched.")
        hint.setProperty("class", "card-desc")
        hint.setWordWrap(True)
        cl.addWidget(hint)
        page.addWidget(card)

        page.addStretch()

    # ── Status helpers ───────────────────────────────────────────────

    def _update_status_display(self, running: bool):
        if running:
            self.status_dot.setText("●")
            self.status_dot.setStyleSheet("color: #00b894; font-size: 18px;")
            self.status_text.setText("Running")
            self.status_text.setObjectName("StatusRunning")
        else:
            self.status_dot.setText("●")
            self.status_dot.setStyleSheet("color: #ff6b6b; font-size: 18px;")
            self.status_text.setText("Stopped")
            self.status_text.setObjectName("StatusStopped")
        self.status_text.style().unpolish(self.status_text)
        self.status_text.style().polish(self.status_text)

    # ── Actions ──────────────────────────────────────────────────────

    def select_region(self):
        region = ScreenCapture.select_region()
        if region:
            self.config["capture"]["region"] = region
            self.region_label.setText(region)
            self.auto_save()
            logger.info(f"Region selected: {region}")

    def update_trans_ui_state(self, backend):
        self.deepl_card.setVisible(backend == "DeepL")
        self.llm_card.setVisible(backend == "OpenAI Compatible LLM")

    def auto_save(self):
        self.config["general"]["source_lang"] = self.source_lang_input.text()
        self.config["general"]["target_lang"] = self.target_lang_input.text()
        self.config["ocr"]["use_gpu"] = self.gpu_check.isChecked()
        self.config["ocr"]["correction_enabled"] = self.correction_check.isChecked()
        self.config["ocr"]["merge_distance"] = self.merge_spin.value()
        self.config["ocr"]["backend"] = self.ocr_backend_combo.currentText()
        self.config["translation"]["backend"] = self.trans_backend_combo.currentText()
        self.config["translation"]["deepl_api_key"] = self.deepl_key_input.text()
        self.config["translation"]["llm_api_base"] = self.llm_url_input.text()
        self.config["capture"]["interval"] = self.interval_spin.value()
        self.config["developer"]["perf_logging"] = self.perf_log_check.isChecked()
        self.config["developer"]["region_check"] = self.region_check_box.isChecked()
        ConfigManager.save_config(self.config)
        logger.info("Settings auto-saved")

    def start_translation(self):
        if not self.config["capture"]["region"]:
            logger.warning("Please select a region first")
            return
        if not self.overlay:
            self.overlay = OverlayWindow()
        self.worker = TranslationWorker(self.config)
        self.worker.translation_complete.connect(self.update_overlay)
        self.worker.error_occurred.connect(self.show_error_message)
        self.worker.start()
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self._update_status_display(True)
        logger.info("Translation started")

    def stop_translation(self):
        if self.worker:
            self.worker.stop()
            self.worker.wait()
            self.worker = None
        if self.overlay:
            self.overlay.close()
            self.overlay = None
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self._update_status_display(False)
        logger.info("Translation stopped")

    def update_overlay(self, blocks):
        if self.overlay:
            self.overlay.set_text_blocks(blocks)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            if self.overlay:
                self.overlay.close()
                self.overlay = None
                logger.info("Overlay closed via ESC key")

    def closeEvent(self, event):
        self.stop_translation()
        event.accept()

    def show_error_message(self, message):
        from PyQt6.QtWidgets import QMessageBox
        self.stop_translation()
        QMessageBox.critical(self, "OCR Initialization Error", message)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = SettingsWindow()
    window.show()
    sys.exit(app.exec())
