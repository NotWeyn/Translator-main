# Active Context

## Current Focus
- **Project Status**: Production-ready with modern UI redesign completed.
- **Latest Work**: Complete UI redesign of `settings.py` — replaced basic 2008-era look with modern, premium interface. Created `theme.py` module for centralized theme management.
- **Active Issues**: Fixed Wayland black screen in overlay mode by forcing XCB (XWayland) platform.

## Recent Decisions & Changes (Latest Session)
- **UI Redesign**: Completely rewrote `SettingsWindow` in `settings.py` with modern design:
  - Custom sidebar (220px) with emoji icons, app branding, and active nav state
  - Card-based layout with `QFrame` + `QGraphicsDropShadowEffect`
  - Scrollable content pages with header + description
  - Premium form controls (rounded borders, focus states, hover effects)
  - Status indicator with colored dot (green=running, red=stopped)
- **Theme System**: Created `src/ui/theme.py` — centralized dark/light theme with full QSS generation.
  - Dark mode: deep navy-black (#0f0f14) with purple accent (#6c5ce7)
  - Light mode: soft gray (#f0f0f5) with same purple accent
  - Both themes are polished and premium-feeling
- **All functionality preserved**: auto_save, start/stop, select_region, backend switching, theme toggle — all work exactly as before.

## Operating Mode
- **GUI Mode** (default): `./start.sh` → Modern SettingsWindow with sidebar navigation
- **Overlay Mode**: `./start.sh --overlay` → Headless fullscreen overlay, click-through, bbox-based text rendering. Natively supports Wayland compositors (Hyprland, KDE Plasma, Gamescope) without relying solely on X11 or compositor-specific rules.

## Implementation Patterns
- **Theme Module**: `src/ui/theme.py` — `build_stylesheet(theme)` generates complete QSS
- **Card Pattern**: `_make_card(title, desc)` helper creates styled QFrame cards with shadow
- **Nav System**: QPushButton-based sidebar with dynamic class toggling (`nav-item` / `nav-active`)
- **Config Persistence**: TOML file in project root, auto-save on settings change.
- **Threading**: Translation worker runs in `QThread` to avoid blocking UI.
- **Performance Logging**: Timing each step (Capture/OCR/Process/Translate) when enabled.
- **Text Clustering**: Configurable merge distance, punctuation-aware separation.
- **Overlay Rendering**: Dual-mode paint: windowed (linear list) vs overlay (bbox-based with background darkening).

## Developer Tools
1. **Performance Logging**: Console output showing timing for each pipeline step
2. **Region Checker**: Shows raw OCR output without translation (debug mode)

## Known Technical Details
- **Config File**: `config.toml` at project root (auto-created, `.gitignore`'d)
- **Text Processing**: Clustering happens before display, affecting both modes
- **Overlay Mode**: Each text block rendered at its bbox position with configurable background
- **Theme Module**: `src/ui/theme.py` with `DARK` and `LIGHT` palette dicts

## Next Steps
1. Implement global hotkey support for overlay mode (`[hotkeys]` section).
2. Investigate multiplatform packaging.
