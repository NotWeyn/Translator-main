# ⚙️ Yapılandırma — `config.toml`

Uygulama ilk çalıştığında otomatik olarak proje kökünde bir `config.toml` dosyası oluşturur. Elle düzenleyebilir veya GUI üzerinden ayarlayabilirsiniz.

---

## Tam Şema

```toml
[general]
source_lang = "auto"          # Otomatik dil algılama
target_lang = "tr"            # Hedef dil
theme = "dark"                # "dark" | "light"

[ocr]
backend = "EasyOCR"           # "EasyOCR" | "PaddleOCR"
use_gpu = true                # GPU hızlandırma (CUDA gerekir)
correction_enabled = true     # Yazım düzeltme
merge_distance = 20           # Metin birleştirme mesafesi (piksel)

[translation]
backend = "Argos Translate"   # "Argos Translate" | "OpenAI Compatible LLM" | "Google" | "DeepL"
openai_api_key = ""
deepl_api_key = ""
llm_api_base = "http://127.0.0.1:5000/v1"

[capture]
region = ""                   # slurp ile seçilen bölge ("x,y wxh")
interval = 5                  # Tarama aralığı (saniye)

[overlay]
enabled = false               # Overlay varsayılan durumu
background_opacity = 0.75     # Yazı arkası karartma (0.0 = şeffaf, 1.0 = tam siyah)
background_color = "#000000"  # Karartma rengi
background_padding = 4        # Yazı etrafındaki boşluk (piksel)
font_family = "Arial"         # Yazı tipi
font_size = 14                # Yazı boyutu
font_color = "#FFFFFF"        # Yazı rengi
font_bold = false             # Kalın yazı
target_region = ""            # Overlay'e özel bölge (boş = capture.region kullanılır)
always_on_top = true          # Her zaman en üstte
click_through = true          # Tıklamalar overlay'den geçer
show_original = false         # Orijinal metni çevirinin yanında göster
refresh_interval = 3          # Overlay yenileme aralığı (saniye)

[hotkeys]
toggle_overlay = "Ctrl+Shift+T"   # Overlay aç/kapa
select_region = "Ctrl+Shift+R"    # Bölge seçimi
stop_translation = "Escape"       # Çeviriyi durdur

[developer]
perf_logging = false          # Performans loglaması (terminale yazdırır)
region_check = false          # OCR debug modu (sadece ham metin göster)
log_level = "INFO"            # "DEBUG" | "INFO" | "WARNING" | "ERROR"
```

---

## Bölüm Açıklamaları

### `[general]`
Temel dil ve tema ayarları. `source_lang = "auto"` otomatik dil algılama yapar.

### `[ocr]`
OCR motoru seçimi ve ince ayarlar.

- **`merge_distance`**: Yakın metin bloklarını birleştirme mesafesi. Yüksek çözünürlüklerde artırın:

| Çözünürlük | Önerilen |
|------------|----------|
| 1080p | `20–50` |
| 1440p | `50–100` |
| 4K | `100–200` |

### `[translation]`
Çeviri motoru ve ilgili kimlik bilgileri. Backend'e göre yalnızca ilgili alanlar kullanılır.

### `[capture]`
Ekran yakalama bölgesi ve tarama sıklığı. `region` alanı GUI'den **Select Region** butonuyla veya `slurp` çıktısıyla doldurulur.

### `[overlay]`
Overlay modunun tüm görsel ve davranışsal ayarları.

- **`background_opacity`**: `0.0` tamamen şeffaf, `1.0` tamamen opak siyah arka plan.
- **`target_region`**: Boş bırakılırsa `[capture].region` kullanılır. Overlay için farklı bir bölge izlemek istiyorsanız doldurun.
- **`show_original`**: `true` yaparsanız, çevrilen metnin üstünde orijinal metin küçük yazıyla gösterilir.
- **`refresh_interval`**: `[capture].interval`'den bağımsız — overlay'in ne sıklıkla güncelleneceğini belirler.

### `[hotkeys]`
Global kısayol tuşları. *(Şu an tanımlı ancak aktif implementasyon gelecek sürümde eklenecek.)*

### `[developer]`
Geliştirici araçları.

- **`perf_logging`**: Her çeviri döngüsünün adım adım süresini terminale yazdırır.
- **`region_check`**: Çeviri yapmadan sadece OCR çıktısını gösterir — doğruluk testi için kullanışlı.
