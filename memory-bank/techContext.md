# Tech Context

## Development Environment
- **OS**: Arch Linux
- **Window Manager**: Hyprland (Wayland)
- **Language**: Python 3.x

## Dependencies
- **GUI**: `PyQt6`
- **OCR**: `paddlepaddle-gpu` (or cpu), `paddleocr`, `easyocr`, `torch` (for EasyOCR)
- **Image Processing**: `opencv-python`, `numpy`, `Pillow`
- **System Interaction**: `subprocess` (for calling grim/slurp)
- **API**: `openai`, `requests`

## External Tools
- `grim`: Screenshot utility for Wayland.
- `slurp`: Region selection utility for Wayland.
- `wl-clipboard`: Clipboard interaction (optional but useful).

## Constraints
- **Wayland Security**: Cannot arbitrarily spy on other windows. Must use portal or specific tools like `grim`.
- **Performance**: OCR and LLM inference can be heavy. GPU acceleration is preferred if available.
