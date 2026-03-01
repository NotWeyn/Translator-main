# Project Task Checklist

## Phase 1: Environment & Core Logic
- [x] **Setup**: Create `requirements.txt` with dependencies (PyQt6, PaddleOCR, EasyOCR, OpenAI, ArgosTranslate, etc.).
- [x] **OCR Module**:
    - [x] Create `OCRBackend` abstract base class.
    - [x] Implement `PaddleBackend`.
    - [x] Implement `EasyOCRBackend`.
- [x] **Text Processing**:
    - [x] Implement text clustering algorithm (grouping nearby bounding boxes).
    - [x] Implement basic correction logic.
- [x] **Translation Module**:
    - [x] Create `TranslatorBackend` abstract base class.
    - [x] Implement `OpenAITranslator`.
    - [x] Implement `OfflineTranslator` (Argos Translate).
    - [x] Implement `GoogleTranslator` & `DeepLTranslator`.

## Phase 2: Screen Capture & Overlay (Wayland)
- [x] **Capture Utils**:
    - [x] Implement `grim` wrapper for screenshots.
    - [x] Refactor `main.py` to launch GUI by default
- [x] Implement Settings GUI
    - [x] Add Region Selection
    - [x] Add Interval Setting (ticks)
    - [x] Add Start/Stop Buttons
    - [x] Implement Auto-save
    - [x] Remove Save Button
    - [x] Add Hyprland Mode Toggle
- [x] Create Translation Worker (Thread/Timer)
- [x] Fix Overlay Window for Hyprland
- [x] Signal handling for Ctrl+C
- [x] Rename "Offline" to "Yerel Çeviri"
- [x] **Overlay UI**:
    - [x] Create transparent PyQt6 window.
    - [x] Implement "click-through" functionality.
    - [x] Implement text drawing logic (placing translated text over original).

## Phase 3: Settings UI & Integration
- [x] **Settings Interface**:
    - [x] Implement configuration saving/loading.
    - [x] Design tabbed UI (General, OCR, Translation, Appearance).
- [x] **Main Application**:
    - [x] Connect Global Hotkeys (or system trigger).
    - [x] Integrate Capture -> OCR -> Process -> Translate -> Overlay pipeline.

## Phase 4: Verification & Polish
- [x] **Testing**:
    - [x] Verify OCR accuracy on game screenshots.
    - [x] Verify Offline Translation works without internet.
    - [x] Verify Overlay alignment and performance.
- [x] **Documentation**:
    - [x] Write usage guide.

## Phase 5: Refinements & Fixes
- [x] **Core Fixes**:
    - [x] Fix PaddleOCR `Unknown argument: show_log` error.
    - [x] **Fix PaddleOCR Protobuf Error**: `Invalid default '0.8'`. Pin `protobuf<=3.20.3`.
    - [x] **Fix PaddleOCR `cls` Argument Error**: Remove `cls=True` from `ocr()` call.
- [x] **Performance & Debugging**:
    - [x] Add "Developer" tab/menu.
    - [x] Implement "Performance Logging" (Capture -> OCR -> Translate -> Overlay timings).
    - [x] **Implement Region Checker (OCR Debug)**: Show detected text without translation.
- [x] **Text Processing Fixes**:
    - [x] **Fix Text Overflow**: Translated text exceeds original box size. Implement dynamic box resizing.
    - [x] **Fix Clustering Logic**: "Merge Distance" not effective. Improve paragraph/sentence detection heuristics.
- [x] **Overlay Enhancements**:
    - [x] Ensure "click-through" works for background interaction (`WindowTransparentForInput`).
    - [x] Fix text overflow in translation boxes (wrapping/sizing).
    - [x] **Refactor Non-Hyprland Mode**:
        - [x] Switch from "Overlay" to "Windowed" mode.
        - [x] Display text linearly/centered in the window instead of using absolute screen coordinates.
        - [x] Auto-resize font when text is too long (prevent overflow).
- [x] **UI Polish**:
    - [x] Rename "Check Interval (ticks)" to "(seconds)".
    - [x] Add Dark/Light Theme Toggle.
    - [x] Update `README.md` and `AGENTS.md`.
- [x] **kullanıcı talepleri**:
    - [x] translation seçeneklerindeki openai seçeneği komple kaldırılsın gerek yok
    - [x] local translation argos translate adı ile değiştirilecek
    - [x] openai api key ve deepl api key sadece traslation backend de onların seçenekleri seçildiğinde aktif olacak
    - [x]  local ai diye isimlendirdiğimizin adını openai compatible llm ile değiştirelim   
        - [x] bu seçenek seçildiğinde bir alt girdi açılacak ve buraya local ai portu giirlecek http://127.0.0.1:5000 gibi , sadece sondaki 5000 portunu istemeyeceğiz bütün http uzantısını alalım ki kullanabilelim 
        - [x] ERROR:src.core.translator:Local AI Translation failed: 404 Client Error: Not Found for url: http://127.0.0.1:5000/translate
        şeklinde bir hata döndürüyor çünkü istek şekli hatalı düzeltilmeli
    - [x] argos traslate seçildiğinde en->tr şeklinde bir girdi tarzı kabul etmiyor ona farklı bir çözüm bulunmalı kısaca çeviri yapmıyor neye çevireceğini çözemediği için uyumlu değil diyelim 
    - [x] region checker seçildiğinde tespit edilen her cümlenin başına OCR yazdırılmasın sadece saf cümle yazdırılsın
    - [x] docker komple kaldırılsın (docker desteği kaldırılacak)
    - [x] argos translate kütüphaneleri seçilen dile göre otomatik indirilsin (readme den manuel talimat kaldırılsın)
    - [x] paddleocr komple kaldırılsın (sadece easyocr kalacak)
    - [x] **Fix Hyprland Overlay**:
        - [x] Ensure click-through works (pass input to background apps).
        - [x] Ensure visibility of background apps (transparency).
