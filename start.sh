#!/bin/bash
# ─────────────────────────────────────────────────────────
#  Linux Screen Translator — Launcher Script
#  Konsol penceresi göstermeden sadece GUI'yi açar.
# ─────────────────────────────────────────────────────────

# Script'in bulunduğu dizine geç
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# ── Terminalden çalıştırıldıysa, arka plana at ve terminali kapat ──

# ── Hata mesajı gösterme (GUI dialog) ──
show_error() {
    local msg="$1"
    if command -v zenity &>/dev/null; then
        zenity --error --title="Screen Translator" --text="$msg" --no-wrap 2>/dev/null
    elif command -v kdialog &>/dev/null; then
        kdialog --error "$msg" --title "Screen Translator" 2>/dev/null
    elif command -v notify-send &>/dev/null; then
        notify-send -u critical "Screen Translator — Hata" "$msg"
    fi
}

# ── Sistem bağımlılıkları kontrolü ──
MISSING_DEPS=()

command -v python3 &>/dev/null || MISSING_DEPS+=("python3")
command -v grim &>/dev/null    || MISSING_DEPS+=("grim")
command -v slurp &>/dev/null   || MISSING_DEPS+=("slurp")
python3 -c "import PyQt6" &>/dev/null || MISSING_DEPS+=("python-pyqt6")

if [ ${#MISSING_DEPS[@]} -ne 0 ]; then
    show_error "Eksik sistem bağımlılıkları:\n${MISSING_DEPS[*]}\n\nKurmak için:\nsudo pacman -S ${MISSING_DEPS[*]}"
    exit 1
fi

# ── Venv sağlık kontrolü (taşınmış/bozuk venv tespiti) ──
if [ -d "venv" ]; then
    if ! ./venv/bin/python3 --version &>/dev/null; then
        rm -rf venv
    fi
fi

# ── Venv yoksa oluştur ve bağımlılıkları kur ──
if [ ! -d "venv" ]; then
    if command -v zenity &>/dev/null; then
        (
        echo "10"; echo "# Sanal ortam (venv) oluşturuluyor..."
        python3 -m venv venv --system-site-packages || exit 1
        echo "30"; echo "# Hızlı kurulum için 'uv' paket yöneticisi indiriliyor..."
        ./venv/bin/pip install uv -q || exit 1
        echo "60"; echo "# Gerekli kütüphaneler indiriliyor (Bu işlem internet hızınıza göre sürebilir)..."
        VIRTUAL_ENV="$PWD/venv" ./venv/bin/uv pip install -r requirements.txt -q || exit 1
        echo "100"; echo "# Kurulum tamamlandı!"
        ) | zenity --progress --title="Screen Translator - İlk Kurulum" --text="Hazırlanıyor..." --percentage=0 --auto-close --auto-kill --width=400
        
        if [ ${PIPESTATUS[0]} -ne 0 ]; then
            show_error "Bağımlılıklar yüklenirken veya iptal edildiği için hata oluştu."
            rm -rf venv
            exit 1
        fi
    elif command -v kdialog &>/dev/null; then
        dbusRef=$(kdialog --progressbar "Screen Translator İlk Kurulum\nSanal ortam (venv) oluşturuluyor..." 100 --title "İlk Kurulum")
        qdbus $dbusRef Set "" value 10 2>/dev/null
        python3 -m venv venv --system-site-packages
        if [ $? -eq 0 ]; then
            qdbus $dbusRef setLabelText "Hızlı kurulum için 'uv' indiriliyor..." 2>/dev/null
            qdbus $dbusRef Set "" value 30 2>/dev/null
            ./venv/bin/pip install uv -q
            if [ $? -eq 0 ]; then
                qdbus $dbusRef setLabelText "Gerekli kütüphaneler indiriliyor (Bu işlem sürebilir)..." 2>/dev/null
                qdbus $dbusRef Set "" value 60 2>/dev/null
                VIRTUAL_ENV="$PWD/venv" ./venv/bin/uv pip install -r requirements.txt -q
                if [ $? -eq 0 ]; then
                    qdbus $dbusRef Set "" value 100 2>/dev/null
                    sleep 1
                else
                    show_error "Kütüphaneler yüklenirken hata oluştu."
                    rm -rf venv
                    exit 1
                fi
            else
                show_error "uv yüklenirken hata oluştu."
                rm -rf venv
                exit 1
            fi
        else
            show_error "Venv oluşturulurken hata oluştu."
            rm -rf venv
            exit 1
        fi
        qdbus $dbusRef close 2>/dev/null
    else
        # Fallback if no GUI dialog
        command -v notify-send &>/dev/null && notify-send "Screen Translator" "İlk kurulum yapılıyor, sanal ortam ve bağımlılıklar indiriliyor..."
        python3 -m venv venv --system-site-packages
        ./venv/bin/pip install uv -q
        VIRTUAL_ENV="$PWD/venv" ./venv/bin/uv pip install -r requirements.txt -q
        
        if [ $? -ne 0 ]; then
            show_error "Bağımlılıklar yüklenirken hata oluştu."
            rm -rf venv
            exit 1
        fi
        command -v notify-send &>/dev/null && notify-send "Screen Translator" "İlk kurulum tamamlandı."
    fi
fi

# ── requirements.txt değişmişse bağımlılıkları güncelle ──
CURRENT_HASH=$(md5sum requirements.txt 2>/dev/null | cut -d' ' -f1)
STORED_HASH=""
[ -f ".deps_hash" ] && STORED_HASH=$(cat .deps_hash)

if [ "$CURRENT_HASH" != "$STORED_HASH" ]; then
    if command -v zenity &>/dev/null; then
        (
        echo "50"; echo "# Yeni bağımlılıklar uv ile güncelleniyor..."
        VIRTUAL_ENV="$PWD/venv" ./venv/bin/uv pip install -r requirements.txt -q || exit 1
        echo "100"; echo "# Güncelleme tamamlandı!"
        ) | zenity --progress --title="Screen Translator - Güncelleme" --text="Bağımlılıklar güncelleniyor..." --percentage=0 --auto-close --auto-kill --width=400
    elif command -v kdialog &>/dev/null; then
        dbusRef=$(kdialog --progressbar "Screen Translator Güncelleme\nYeni bağımlılıklar uv ile güncelleniyor..." 100)
        qdbus $dbusRef Set "" value 50 2>/dev/null
        VIRTUAL_ENV="$PWD/venv" ./venv/bin/uv pip install -r requirements.txt -q
        qdbus $dbusRef Set "" value 100 2>/dev/null
        sleep 1
        qdbus $dbusRef close 2>/dev/null
    else
        VIRTUAL_ENV="$PWD/venv" ./venv/bin/uv pip install -r requirements.txt -q 2>/dev/null || ./venv/bin/pip install -r requirements.txt -q 2>/dev/null
    fi
    echo "$CURRENT_HASH" > .deps_hash
fi

# ── Uygulamayı başlat ──
exec ./venv/bin/python main.py "$@"
