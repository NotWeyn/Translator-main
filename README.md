<p align="center">
  <h1 align="center">🌐 Screen Translator</h1>
  <p align="center">
    <em>Linux masaüstünde gerçek zamanlı ekran çevirisi — oyunlar, uygulamalar ve her şey için.</em>
  </p>
  <p align="center">
    <img src="https://img.shields.io/badge/platform-Linux-blue?style=flat-square" alt="Platform">
    <img src="https://img.shields.io/badge/Wayland-ready-green?style=flat-square" alt="Wayland">
    <img src="https://img.shields.io/badge/Python-3.10+-yellow?style=flat-square" alt="Python">
    <img src="https://img.shields.io/badge/license-MIT-lightgrey?style=flat-square" alt="License">
  </p>
</p>

---

## ✨ Ne Yapıyor?

Ekranınızdaki herhangi bir bölgeyi seçin — uygulama o bölgedeki metni **algılar**, **anlar** ve seçtiğiniz dile **çevirir**. Oyun oynarken, belge okurken veya yabancı dilde bir uygulama kullanırken çalışır.

**İki mod:**

| Mod | Açıklama | Başlatma |
|-----|----------|----------|
| 🖥️ **GUI Modu** | Ayar penceresi + pencereli çeviri görünümü | `./start.sh` |
| 🎮 **Overlay Modu** | Tam ekran, tıklama-geçiren şeffaf katman — metin doğrudan üzerine yazılır | `./start.sh --overlay` |

---

## 🚀 Hızlı Başlangıç

### 1. Sistem Bağımlılıkları

```bash
# Arch Linux / Manjaro
sudo pacman -S grim slurp python-pyqt6

# GPU hızlandırma (EasyOCR için önerilir)
sudo pacman -S cuda cudnn
```

### 2. Başlat

```bash
git clone <repo-url> && cd Translator-main
./start.sh
```

`start.sh` gerisini halleder: sanal ortamı oluşturur, bağımlılıkları kurar ve uygulamayı başlatır. İlk çalıştırmada birkaç dakika sürebilir.

> **Overlay modu** için: `./start.sh --overlay`  
> Tüm ayarlar proje kökündeki `config.toml` dosyasından okunur.

---

## ⚙️ Yapılandırma

Uygulama ilk çalıştığında proje kökünde otomatik olarak bir `config.toml` dosyası oluşturur. Elle düzenleyebilir veya GUI üzerinden ayarlayabilirsiniz.

**Bölümler:** `[general]` · `[ocr]` · `[translation]` · `[capture]` · `[overlay]` · `[hotkeys]` · `[developer]`

> 📄 **Tüm ayarlar, açıklamalar ve önerilen değerler için:** [docs/CONFIGURATION.md](docs/CONFIGURATION.md)

---

## 📖 Kullanım Kılavuzu

### GUI Modu

1. `./start.sh` ile uygulamayı başlatın
2. **Select Region** → Ekrandan çevrilecek bölgeyi sürükleyerek seçin
3. **Start Translation** → Çeviri başlar, sonuçlar pencereli overlay'de gösterilir
4. **Stop** → Durdurur

**Sidebar menüsünden erişilebilen sekmeler:**

| Sekme | İçerik |
|-------|--------|
| **Control** | Bölge seçimi, başlat/durdur, tema değiştirme |
| **General** | Kaynak ve hedef dil ayarları |
| **OCR** | Backend seçimi, GPU, metin birleştirme mesafesi |
| **Translation** | Çeviri motoru, API anahtarları |
| **Developer** | Performans logları, OCR debug modu |

### Overlay Modu

```bash
./start.sh --overlay
```

- GUI açılmaz — doğrudan fullscreen şeffaf overlay başlar
- Belirlenen bölgedeki metinler algılanıp **bbox üzerine** karartmalı arka planla çevrilir
- Tıklamalar overlay'den geçer (oyun/uygulama kullanımını engellemez)
- Durdurmak için: `Ctrl+C` veya `ESC`

> **İpucu:** Overlay ayarlarını (`config.toml → [overlay]`) düzenleyerek arka plan opaklığı, yazı tipi, renk ve boyut gibi değerleri özelleştirin.

---

## 🔧 Çeviri Motorları

| Motor | Tür | Not |
|-------|-----|-----|
| **Argos Translate** | Offline | Modeller otomatik indirilir, internet gerekmez |
| **OpenAI Compatible LLM** | Lokal/API | Ollama, LM Studio veya herhangi bir uyumlu endpoint |
| **Google Translate** | Online | API anahtarı gerekmez |
| **DeepL** | Online | API anahtarı gerekir |

---

## 🔍 Sorun Giderme

### Metin doğru birleşmiyor / cümleler bölünüyor

**Text Merge Distance** değerini artırın (`config.toml → [ocr] → merge_distance`):

| Çözünürlük | Önerilen Değer |
|------------|---------------|
| 1080p | `20–50` |
| 1440p | `50–100` |
| 4K | `100–200` |

> Noktalama işaretlerinden (`.`, `!`, `?`) sonra birleştirme hassasiyeti otomatik olarak düşer — bu, farklı cümlelerin yanlışlıkla birleşmesini önler.

### Wayland sorunları

```bash
# grim ve slurp'ın çalıştığını doğrulayın
grim test.png && echo "grim OK"
slurp && echo "slurp OK"
```

### OCR doğruluğu düşük

- GPU'yu etkinleştirin (`[ocr] → use_gpu = true`)
- Farklı OCR backend deneyin (EasyOCR ↔ PaddleOCR)
- **Developer → Region Checker** ile ham OCR çıktısını inceleyin

---

## 🏗️ Mimari

```
Screen Translator
├── start.sh              ← Başlatıcı (venv + bağımlılık yönetimi)
├── main.py               ← Giriş noktası (--overlay flag)
├── config.toml           ← Tüm ayarlar (otomatik oluşturulur)
├── src/
│   ├── core/
│   │   ├── ocr.py        ← OCR backend'ler (EasyOCR, PaddleOCR)
│   │   ├── text_processor.py  ← Metin kümeleme & düzeltme
│   │   └── translator.py ← Çeviri backend'ler
│   ├── ui/
│   │   ├── settings.py   ← GUI ayar penceresi
│   │   ├── overlay.py    ← Overlay penceresi (dual-mode rendering)
│   │   └── overlay_app.py ← Headless overlay uygulaması
│   └── utils/
│       ├── config.py     ← TOML config yöneticisi
│       └── capture.py    ← grim/slurp sarmalayıcı
```

---

## 📄 Lisans

MIT License — istediğiniz gibi kullanın, değiştirin, dağıtın.
