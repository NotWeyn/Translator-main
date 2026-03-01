# Linux Screen Translator - Walkthrough & Usage Guide

## Installation

### 1. System Dependencies

You need to install the following packages for screen capturing and GUI support:

```bash
sudo pacman -S grim slurp python-pyqt6
```

If you plan to use GPU acceleration (Recommended for EasyOCR):
```bash
sudo pacman -S cuda cudnn
```

### 2. Python Dependencies
Install the required Python libraries:

```bash
pip install -r requirements.txt
```

## Usage

### Configuration
Run the application to open the configuration window:

```bash
python main.py 
```

Here you can:
- **General**: Set source and target languages 
- **OCR**: EasyOCR is used by default. Enable GPU if available.
- **Translation**: 
    - **Argos Translate**: Offline translation (models downloaded automatically).
    - **OpenAI Compatible LLM**: Use local LLMs (Ollama, LM Studio) or compatible APIs.
    - **DeepL / Google**: Web-based translation.

### Running the Translator
1. Run `python main.py` to open the GUI.
2. **Select Region**: Click the button and drag to select the screen area to monitor.
3. **Start Translation**: Click "Start". The app will continuously monitor the region.
4. **Stop**: Click "Stop" to end the session.

### Modes
- **Hyprland Mode (Overlay)**:
    - Best for games/apps where you want text replaced in-place.
    - Uses an overlay window that matches the text positions.
    - *Experimental*: Requires Wayland/Hyprland with specific window rules for click-through.
- **Windowed Mode (Non-Hyprland)**:
    - Best for watching videos or general usage.
    - Opens a separate "Subtitle Window" that lists the translated text.
    - You can move and resize this window freely.

### Developer Tools
- **Performance Logging**: Enable in the "Developer" tab to see timing stats in the terminal.
- **Region Checker**: Enable to see the raw OCR output without translation (useful for debugging OCR accuracy).

## Troubleshooting
- **Wayland Issues**: Ensure `grim` and `slurp` work from your terminal first.
- **OCR Accuracy & Text Merging**: 
    - If text appears split into multiple disconnected lines when it should be one sentence, increase the **"Text Merge Distance"** in Settings → OCR tab.
    - This parameter controls how aggressively the app merges nearby text blocks:
        - **Vertical sensitivity**: Text blocks closer than this distance (in pixels) vertically will be merged.
        - **Horizontal sensitivity**: Also affects horizontal merging (threshold = max(50, merge_distance)).
    - **Recommended values**:
        - `20-50` for 1080p screens
        - `50-100` for 1440p screens
        - `100-200` for 4K screens or when text is very spread out
    - If text still won't merge, the OCR might be detecting them as separate blocks due to punctuation (periods, exclamation marks, question marks). The app reduces merge sensitivity after punctuation to avoid incorrectly merging different sentences.

