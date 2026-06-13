#!/bin/bash

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "Inteligentna Wycena Nieruchomości"

if ! command -v python3 &> /dev/null; then
    echo " Python3 nie jest zainstalowany."
    echo "   Zainstaluj Python 3.10+ ze strony: https://www.python.org/downloads/"
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
echo "Python $PYTHON_VERSION"

if [ ! -d "venv" ]; then
    echo "Tworzenie środowiska wirtualnego..."
    python3 -m venv venv
    echo "Środowisko wirtualne utworzone"
fi

source venv/bin/activate

echo "Instalacja zależności..."
pip install -q --upgrade pip
pip install -q -r requirements.txt
echo "Zależności zainstalowane"

echo ""
echo "Uruchamianie aplikacji..."
echo "   Otwórz przeglądarkę: http://localhost:8000"
echo "   Aby zatrzymać: Ctrl+C"
echo ""

python app/api.py

