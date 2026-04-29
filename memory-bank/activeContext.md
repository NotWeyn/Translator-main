# Active Context

## Current Focus
- **Project Status**: Production-ready with recent bug fixes.
- **Latest Work**: Implemented dynamic OCR backend loading/installation, redesigned the main UI layout to use a collapsible left sidebar, and completely removed the experimental Hyprland mode.
- **Active Issues**: None currently.

## Recent Decisions & Changes (Latest Session)
- **UI Redesign**: Replaced the standard horizontal tab layout with a vertical list inside a collapsible left panel (sidebar) to improve aesthetics and navigation.
- **Dynamic OCR Loading**: OCR backends (EasyOCR, PaddleOCR, MMOCR) are now loaded dynamically when translation starts, rather than at application launch. If a required OCR package is missing, it will be automatically installed via `pip`.
- **Hyprland Mode Removal**: The experimental Hyprland mode (which relied on absolute coordinates and specific compositor transparency features) has been completely removed. The application now exclusively uses the more reliable Windowed mode.

## Operating Mode
- **Windowed Mode**: Linear list with improvements:
  - Dynamic font sizing
  - Visual separators between sentence blocks (gray horizontal lines)
  - Auto-wrapping text

## Implementation Patterns
- **Config Persistence**: Auto-save on any settings change using `ConfigManager`.
- **Threading**: Translation worker runs in `QThread` to avoid blocking UI.
- **Performance Logging**: Timing each step (Capture/OCR/Process/Translate) when enabled.
- **Theme System**: CSS-based styling switchable at runtime.
- **Text Clustering**: Configurable merge distance, punctuation-aware separation.

## Developer Tools
1. **Performance Logging**: Console output showing timing for each pipeline step
2. **Region Checker**: Shows raw OCR output without translation (debug mode)

## Known Technical Details
- **PaddleOCR Compatibility**: 
  - Requires `protobuf<=3.20.3` 
  - `use_angle_cls=True` in initialization only
  - NO `cls` parameter in `ocr()` call
- **Text Processing**: Clustering happens before display, affecting both modes
- **Windowed Mode**: Each text block is a clustered group of sentences

## Known Issues & Limitations
- ccache warning from PaddleOCR is ignorable (compilation cache optimization)
- First-time installation of MMOCR might take several minutes depending on the system.

## Next Steps
1. Refactor `OpenAITranslator` to support custom base URLs.
2. Investigate multiplatform packaging.
