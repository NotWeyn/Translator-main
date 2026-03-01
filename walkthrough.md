# Walkthrough - User Requests Implementation

## Changes

### 1. Backend Renaming & OpenAI Compatible LLM
- **Renamed**: "Local Translation" -> **"Argos Translate"**.
- **Renamed**: "Local AI" -> **"OpenAI Compatible LLM"**.
- **New Field**: Added **"API URL"** input field (defaults to `http://127.0.0.1:5000/v1`).
- **Implementation**: Reused `OpenAITranslator` with a custom `base_url` to ensure compatibility with standard LLM servers (Ollama, LM Studio, etc.) and fix 404 errors.

### 2. Dynamic UI Logic
- The Settings UI now dynamically shows/hides fields based on the selected translation backend:
    - **Argos Translate**: No extra fields.
    - **OpenAI Compatible LLM**: Shows "API URL".
    - **OpenAI**: Shows "OpenAI API Key".
    - **DeepL**: Shows "DeepL API Key".
    - **Google**: No extra fields.

### 3. Multiplatform & Branding
- Removed "Arch" specific branding from the Window Title, README, and Config paths.
- App is now titled **"Screen Translator"** or **"Linux Screen Translator"**.
- Config path changed to `~/.config/screen_translator/config.json`.


### 4. Argos Translate Improvements
- **Automatic Package Management**: Removed manual installation steps. The app now automatically downloads and installs missing language pairs (e.g., `en` -> `tr`) when needed.
- Fixed language code handling to ensure compatibility with Argos Translate's requirements.

### 6. PaddleOCR Removal
- **Removed PaddleOCR**: Due to persistent issues, PaddleOCR support has been completely removed. The application now uses **EasyOCR** exclusively for text detection.
- **Dependency Cleanup**: Removed `paddlepaddle`, `paddleocr`, and `protobuf` from `requirements.txt`.

## Verification Results

### Manual Verification Steps

1.  **UI Interaction**:
    - Launch the application (`python main.py`).
    - Verify Window Title is "Screen Translator".
    - Go to the **Translation** tab.
    - Select **OpenAI Compatible LLM**: Verify "API URL" field appears with default `http://127.0.0.1:5000/v1`.

2.  **OpenAI Compatible LLM**:
    - Point to a local server (e.g., LM Studio or Ollama).
    - Trigger a translation.
    - Verify it works without 404 errors (uses standard OpenAI client).

3.  **Argos Translate**:
    - Select **Argos Translate**.
    - Trigger a translation. It should download the `en->tr` model (if missing) and translate.

4.  **Region Checker**:
    - Go to **Developer** tab.
    - Enable **Region Checker**.
    - Trigger a capture.
    - Verify the text on screen is the raw OCR output without any `[OCR]` prefix.
