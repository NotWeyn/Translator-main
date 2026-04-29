# Active Context

## Current Focus
- **Project Status**: Production-ready with config.toml migration and overlay mode.
- **Latest Work**: Migrated from JSON config to TOML-based config system (`config.toml` in project root). Added `--overlay` CLI flag for headless overlay mode.
- **Active Issues**: None currently.

## Recent Decisions & Changes (Latest Session)
- **Config Migration (JSON → TOML)**: Replaced `~/.config/screen_translator/config.json` with project-local `config.toml`. Full portability — no external config paths.
- **Nested Config Structure**: Config now uses TOML sections: `[general]`, `[ocr]`, `[translation]`, `[capture]`, `[overlay]`, `[hotkeys]`, `[developer]`.
- **Overlay Mode**: New `--overlay` flag. `./start.sh --overlay` launches a fullscreen, click-through overlay without the GUI. Reads all settings from `config.toml`.
- **Auto-creation**: `config.toml` is auto-created with defaults if missing.

## Operating Mode
- **GUI Mode** (default): `./start.sh` → SettingsWindow with sidebar navigation
- **Overlay Mode**: `./start.sh --overlay` → Headless fullscreen overlay, click-through, bbox-based text rendering

## Implementation Patterns
- **Config Persistence**: TOML file in project root, auto-save on settings change.
- **Threading**: Translation worker runs in `QThread` to avoid blocking UI.
- **Performance Logging**: Timing each step (Capture/OCR/Process/Translate) when enabled.
- **Theme System**: CSS-based styling switchable at runtime.
- **Text Clustering**: Configurable merge distance, punctuation-aware separation.
- **Overlay Rendering**: Dual-mode paint: windowed (linear list) vs overlay (bbox-based with background darkening).

## Developer Tools
1. **Performance Logging**: Console output showing timing for each pipeline step
2. **Region Checker**: Shows raw OCR output without translation (debug mode)

## Known Technical Details
- **Config File**: `config.toml` at project root (auto-created, `.gitignore`'d)
- **Text Processing**: Clustering happens before display, affecting both modes
- **Overlay Mode**: Each text block rendered at its bbox position with configurable background

## Next Steps
1. Implement global hotkey support for overlay mode (`[hotkeys]` section).
2. Investigate multiplatform packaging.
