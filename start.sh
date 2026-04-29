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
    python3 -m venv venv --system-site-packages
    ./venv/bin/pip install --upgrade pip -q 2>/dev/null
    ./venv/bin/pip install -r requirements.txt -q 2>/dev/null

    if [ $? -ne 0 ]; then
        show_error "Python bağımlılıkları yüklenirken hata oluştu."
        rm -rf venv
        exit 1
    fi
fi

# ── requirements.txt değişmişse bağımlılıkları güncelle ──
CURRENT_HASH=$(md5sum requirements.txt 2>/dev/null | cut -d' ' -f1)
STORED_HASH=""
[ -f ".deps_hash" ] && STORED_HASH=$(cat .deps_hash)

if [ "$CURRENT_HASH" != "$STORED_HASH" ]; then
    ./venv/bin/pip install -r requirements.txt -q 2>/dev/null
    echo "$CURRENT_HASH" > .deps_hash
fi

# ── Uygulamayı başlat ──
exec ./venv/bin/python main.py "$@"
