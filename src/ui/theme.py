"""
Centralized theme system for Screen Translator UI.
Provides dark/light color palettes and generates complete QSS stylesheets.
"""

DARK = {
    "bg": "#0f0f14",
    "surface": "#1a1a24",
    "surface_hover": "#22222e",
    "sidebar": "#141419",
    "sidebar_hover": "#1e1e28",
    "accent": "#6c5ce7",
    "accent_glow": "#a29bfe",
    "accent_dim": "#4a3fb5",
    "text": "#e8e8ed",
    "text_sec": "#8888a0",
    "success": "#00b894",
    "danger": "#ff6b6b",
    "border": "#2a2a3a",
    "input_bg": "#12121a",
    "input_border": "#33334a",
    "input_focus": "#6c5ce7",
    "card_shadow": "rgba(0,0,0,0.3)",
}

LIGHT = {
    "bg": "#f0f0f5",
    "surface": "#ffffff",
    "surface_hover": "#f5f5fa",
    "sidebar": "#e8e8ef",
    "sidebar_hover": "#dcdce5",
    "accent": "#6c5ce7",
    "accent_glow": "#a29bfe",
    "accent_dim": "#5a4bd6",
    "text": "#1a1a2e",
    "text_sec": "#6c6c80",
    "success": "#00b894",
    "danger": "#ff6b6b",
    "border": "#d0d0da",
    "input_bg": "#f8f8fc",
    "input_border": "#c8c8d5",
    "input_focus": "#6c5ce7",
    "card_shadow": "rgba(0,0,0,0.08)",
}


def get_palette(theme: str) -> dict:
    return DARK if theme == "dark" else LIGHT


def build_stylesheet(theme: str) -> str:
    c = get_palette(theme)
    return f"""
    /* ── Global ── */
    QWidget#CentralWidget {{
        background-color: {c['bg']};
        color: {c['text']};
        font-family: "Segoe UI", "Inter", "SF Pro Display", "Noto Sans", sans-serif;
        font-size: 13px;
    }}

    /* ── Sidebar ── */
    QFrame#Sidebar {{
        background-color: {c['sidebar']};
        border-right: 1px solid {c['border']};
        border-radius: 0px;
    }}
    QLabel#AppTitle {{
        color: {c['text']};
        font-size: 16px;
        font-weight: 700;
        padding: 0px;
    }}
    QLabel#AppSubtitle {{
        color: {c['text_sec']};
        font-size: 10px;
        padding: 0px;
    }}
    QPushButton.nav-item {{
        background-color: transparent;
        color: {c['text_sec']};
        border: none;
        border-radius: 8px;
        padding: 10px 14px;
        text-align: left;
        font-size: 13px;
        font-weight: 500;
    }}
    QPushButton.nav-item:hover {{
        background-color: {c['sidebar_hover']};
        color: {c['text']};
    }}
    QPushButton.nav-active {{
        background-color: {c['accent']};
        color: #ffffff;
        border: none;
        border-radius: 8px;
        padding: 10px 14px;
        text-align: left;
        font-size: 13px;
        font-weight: 600;
    }}
    QPushButton.nav-active:hover {{
        background-color: {c['accent_glow']};
    }}

    /* ── Theme Toggle ── */
    QPushButton#ThemeToggle {{
        background-color: {c['surface']};
        color: {c['text_sec']};
        border: 1px solid {c['border']};
        border-radius: 8px;
        padding: 8px 12px;
        font-size: 12px;
    }}
    QPushButton#ThemeToggle:hover {{
        background-color: {c['surface_hover']};
        color: {c['text']};
    }}

    /* ── Page Header ── */
    QLabel#PageTitle {{
        color: {c['text']};
        font-size: 22px;
        font-weight: 700;
    }}
    QLabel#PageDesc {{
        color: {c['text_sec']};
        font-size: 12px;
    }}

    /* ── Cards ── */
    QFrame.card {{
        background-color: {c['surface']};
        border: 1px solid {c['border']};
        border-radius: 12px;
        padding: 20px;
    }}
    QLabel.card-title {{
        color: {c['text']};
        font-size: 14px;
        font-weight: 600;
    }}
    QLabel.card-desc {{
        color: {c['text_sec']};
        font-size: 11px;
    }}

    /* ── Form Controls ── */
    QLabel.field-label {{
        color: {c['text_sec']};
        font-size: 12px;
        font-weight: 500;
    }}
    QLineEdit {{
        background-color: {c['input_bg']};
        color: {c['text']};
        border: 1px solid {c['input_border']};
        border-radius: 8px;
        padding: 8px 12px;
        font-size: 13px;
        selection-background-color: {c['accent']};
    }}
    QLineEdit:focus {{
        border: 1px solid {c['input_focus']};
    }}
    QComboBox {{
        background-color: {c['input_bg']};
        color: {c['text']};
        border: 1px solid {c['input_border']};
        border-radius: 8px;
        padding: 8px 12px;
        font-size: 13px;
        min-height: 18px;
    }}
    QComboBox:hover {{
        border: 1px solid {c['accent']};
    }}
    QComboBox::drop-down {{
        border: none;
        width: 24px;
    }}
    QComboBox::down-arrow {{
        image: none;
        border-left: 5px solid transparent;
        border-right: 5px solid transparent;
        border-top: 6px solid {c['text_sec']};
        margin-right: 8px;
    }}
    QComboBox QAbstractItemView {{
        background-color: {c['surface']};
        color: {c['text']};
        border: 1px solid {c['border']};
        border-radius: 8px;
        selection-background-color: {c['accent']};
        selection-color: #ffffff;
        padding: 4px;
    }}
    QSpinBox {{
        background-color: {c['input_bg']};
        color: {c['text']};
        border: 1px solid {c['input_border']};
        border-radius: 8px;
        padding: 8px 12px;
        font-size: 13px;
        min-height: 18px;
    }}
    QSpinBox:focus {{
        border: 1px solid {c['input_focus']};
    }}
    QSpinBox::up-button, QSpinBox::down-button {{
        width: 20px;
        border: none;
        background: transparent;
    }}
    QSpinBox::up-arrow {{
        border-left: 4px solid transparent;
        border-right: 4px solid transparent;
        border-bottom: 5px solid {c['text_sec']};
    }}
    QSpinBox::down-arrow {{
        border-left: 4px solid transparent;
        border-right: 4px solid transparent;
        border-top: 5px solid {c['text_sec']};
    }}
    QCheckBox {{
        color: {c['text']};
        font-size: 13px;
        spacing: 8px;
    }}
    QCheckBox::indicator {{
        width: 18px;
        height: 18px;
        border-radius: 4px;
        border: 2px solid {c['input_border']};
        background-color: {c['input_bg']};
    }}
    QCheckBox::indicator:checked {{
        background-color: {c['accent']};
        border: 2px solid {c['accent']};
    }}
    QCheckBox::indicator:hover {{
        border: 2px solid {c['accent']};
    }}

    /* ── Buttons ── */
    QPushButton.btn-primary {{
        background-color: {c['accent']};
        color: #ffffff;
        border: none;
        border-radius: 8px;
        padding: 10px 24px;
        font-size: 13px;
        font-weight: 600;
    }}
    QPushButton.btn-primary:hover {{
        background-color: {c['accent_glow']};
    }}
    QPushButton.btn-primary:disabled {{
        background-color: {c['accent_dim']};
        color: rgba(255,255,255,0.5);
    }}
    QPushButton.btn-danger {{
        background-color: transparent;
        color: {c['danger']};
        border: 1px solid {c['danger']};
        border-radius: 8px;
        padding: 10px 24px;
        font-size: 13px;
        font-weight: 600;
    }}
    QPushButton.btn-danger:hover {{
        background-color: {c['danger']};
        color: #ffffff;
    }}
    QPushButton.btn-danger:disabled {{
        border-color: {c['border']};
        color: {c['text_sec']};
    }}
    QPushButton.btn-secondary {{
        background-color: {c['surface']};
        color: {c['text']};
        border: 1px solid {c['border']};
        border-radius: 8px;
        padding: 10px 20px;
        font-size: 13px;
        font-weight: 500;
    }}
    QPushButton.btn-secondary:hover {{
        background-color: {c['surface_hover']};
        border-color: {c['accent']};
    }}

    /* ── Status ── */
    QLabel#StatusRunning {{
        color: {c['success']};
        font-weight: 600;
        font-size: 13px;
    }}
    QLabel#StatusStopped {{
        color: {c['danger']};
        font-weight: 600;
        font-size: 13px;
    }}
    QLabel#RegionValue {{
        color: {c['text']};
        font-size: 12px;
        font-family: "JetBrains Mono", "Fira Code", monospace;
        background-color: {c['input_bg']};
        border: 1px solid {c['border']};
        border-radius: 6px;
        padding: 6px 10px;
    }}

    /* ── Scroll Area ── */
    QScrollArea {{
        border: none;
        background-color: transparent;
    }}
    QScrollArea > QWidget > QWidget {{
        background-color: transparent;
    }}
    QScrollBar:vertical {{
        background: transparent;
        width: 8px;
        margin: 0;
    }}
    QScrollBar::handle:vertical {{
        background: {c['border']};
        border-radius: 4px;
        min-height: 30px;
    }}
    QScrollBar::handle:vertical:hover {{
        background: {c['text_sec']};
    }}
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
        height: 0px;
    }}
    QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
        background: transparent;
    }}
    """
