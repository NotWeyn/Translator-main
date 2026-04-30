# Progress

## Status
- [x] Project Initialization
- [x] Memory Bank Setup
- [x] Implementation Plan Creation
- [x] Prototype Development
- [x] UI Implementation
- [x] Testing & Refinement
- [x] Bug Fixes & Polish
- [x] Documentation
- [x] Final Bug Fixes (PaddleOCR, Windowed Mode)
- [x] Created .gitignore
- [x] **UI Redesign**: Implemented a collapsible left sidebar layout.
- [x] **Dynamic OCR Loading**: Added support for EasyOCR, PaddleOCR with automatic installation.
- [x] **Hyprland Mode Removal**: Streamlined the application by removing experimental Wayland-specific features.
- [x] **Config Migration**: Replaced JSON config with TOML-based `config.toml` in project root.
- [x] **Overlay Mode**: Added `--overlay` CLI flag for headless fullscreen overlay.
- [x] **Modern UI Redesign v2**: Complete premium redesign — sidebar with icons, card layout, theme module, polished dark/light modes.
- [x] **Launcher Enhancements**: Added GUI progress dialog (zenity/kdialog) to `start.sh` and integrated `uv` for fast initial setup.

## What Works
### Core Functionality
- **Screen Capture**: `grim` + `slurp` for region selection.
- **OCR**: EasyOCR, PaddleOCR backends working with dynamic loading/installation.
- **Text Processing**: Clustering with configurable merge distance, punctuation awareness.
- **Translation**: OpenAI, Google, DeepL, Argos Translate backends.
- **Overlay System**: Windowed mode + new overlay mode (bbox-based rendering).

### Config System
- **TOML-based**: `config.toml` in project root for full portability.
- **Auto-creation**: File created with defaults if missing.
- **Sections**: `[general]`, `[ocr]`, `[translation]`, `[capture]`, `[overlay]`, `[hotkeys]`, `[developer]`.
- **Deep merge**: Missing keys auto-filled from defaults.

### Overlay Mode (`--overlay`)
- **Fullscreen, click-through** transparent window (Natively supported on Hyprland, KDE Plasma, Gamescope).
- **Configurable**: background opacity/color/padding, font family/size/color/bold.
- **Show original text** option alongside translation.
- **Separate refresh interval** from capture interval.
- **Target region** override for overlay-specific capture area.

### UI Features
- **Modern Settings GUI**: Premium sidebar with icons, card-based content layout.
- **Theme System**: `src/ui/theme.py` — centralized dark/light with purple accent (#6c5ce7).
- **Auto-save**: Settings persist to `config.toml` automatically.
- **Theme Toggle**: Dark/Light mode switching with polished themes.
- **Status Indicator**: Colored dot (green/red) for translation state.

## Known Issues & Limitations
- **Hotkeys**: `[hotkeys]` section is defined in config but not yet implemented (future work).
- **PaddleOCR**: ccache warning is normal (can be ignored).

## Future Considerations
- Implement global hotkey support for overlay toggle/region select
- Packaging for distribution (AUR, standalone binary)
- Performance optimizations for low-end hardware
