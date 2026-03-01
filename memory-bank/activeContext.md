# Active Context

## Current Focus
- **Project Status**: Production-ready with recent bug fixes.
- **Latest Work**: Fixed PaddleOCR compatibility and improved Windowed Mode visual separation.
- **Active Issues**: Ensuring text blocks are visually distinct in Windowed Mode.

## Recent Decisions & Changes (Latest Session)
- **PaddleOCR Fix (Final)**: Completely removed `cls=True` parameter from `ocr()` call (previous fix was incomplete - had duplicate line).
- **Windowed Mode Separation**: Added horizontal separator lines between text blocks for better visual distinction.
- **Text Merge Distance**: Works correctly - affects how OCR results are clustered before display.

## Two Operating Modes
- **Hyprland Mode** (Experimental): Overlay at exact screen positions
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
- Hyprland Mode click-through depends on compositor support
- ccache warning from PaddleOCR is ignorable (compilation cache optimization)

## Next Steps
1. Rename "Local AI" to "OpenAI Compatible LLM" and switch to URL input.
2. Refactor `OpenAITranslator` to support custom base URLs.
3. Remove "Arch" branding from UI and docs.
4. Investigate multiplatform packaging.
