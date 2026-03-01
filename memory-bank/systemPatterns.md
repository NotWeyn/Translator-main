# System Patterns

## Architecture
The application follows a modular pipeline architecture:

1.  **Trigger Service**: Listens for global hotkeys (likely via `hyprland` binds or a global input listener if possible, but Hyprland binds invoking a script is safer/easier).
2.  **Capture Module**: Wraps `grim` and `slurp` to get screenshots.
3.  **OCR Service**: Abstract Strategy pattern to switch between `PaddleOCR` and `EasyOCR`.
4.  **Text Processor**:
    *   **Clustering**: Algorithm to group bounding boxes based on proximity and alignment.
    *   **Correction**: Spell checker and/or LLM-based correction.
5.  **Translation Service**: Abstract Strategy pattern for `OpenAI`, `DeepL`, `Local`.
6.  **UI/Overlay**:
    *   **Settings Window**: PyQt6 application for configuration.
    *   **Overlay Window**: Transparent, click-through PyQt6 window that draws translated text over the screen.

## Key Technical Decisions
- **Wayland Compatibility**: Using command-line tools (`grim`) for capture avoids Wayland security restrictions on direct screen access.
- **PyQt6**: Chosen for robust GUI capabilities and cross-platform potential (though currently focused on Linux).
- **Async/Threading**: OCR and Translation are blocking I/O operations; they must run in background threads to keep the UI responsive.

## Design Patterns
- **Strategy Pattern**: For interchangeable backends (OCR, Translation).
- **Observer Pattern**: To update the UI/Overlay when translation completes.
- **Singleton**: Configuration manager to ensure settings are consistent across modules.
