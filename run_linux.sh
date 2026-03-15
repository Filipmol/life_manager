#!/usr/bin/env bash
set -e

echo "============================================================"
echo "         Ultimate Daily Life Manager - Launcher"
echo "============================================================"
echo ""

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# ── Check Python ─────────────────────────────────────────────────
if command -v python3 &>/dev/null; then
    PY=python3
elif command -v python &>/dev/null; then
    PY=python
else
    echo "[ERROR] Python 3 is not installed."
    echo ""
    echo "Install it with your package manager:"
    echo "  Ubuntu/Debian:  sudo apt install python3 python3-pip python3-venv"
    echo "  Fedora:         sudo dnf install python3 python3-pip"
    echo "  Arch:           sudo pacman -S python python-pip"
    echo ""
    exit 1
fi

echo "[OK] Python found: $($PY --version)"
echo ""

# ── Create virtual environment (keeps system clean) ──────────────
if [ ! -d ".venv" ]; then
    echo "[..] Creating virtual environment..."
    $PY -m venv .venv
fi

source .venv/bin/activate
echo "[OK] Virtual environment activated."
echo ""

# ── Install / upgrade dependencies ───────────────────────────────
echo "[..] Installing dependencies..."
pip install --upgrade pip -q
pip install -r requirements.txt -q
echo "[OK] Dependencies installed."
echo ""

# ── Check Ollama (non-blocking) ──────────────────────────────────
echo "[..] Checking if Ollama is running..."
if curl -s http://localhost:11434/api/tags >/dev/null 2>&1; then
    echo "[OK] Ollama is running."
else
    echo "[!!] Ollama is NOT running. AI features will be unavailable."
    echo "     To enable AI, install Ollama:"
    echo "       curl -fsSL https://ollama.com/install.sh | sh"
    echo "     Then run:  ollama pull llama3.2"
fi
echo ""

# ── Launch the app ───────────────────────────────────────────────
echo "============================================================"
echo "  Starting Life Manager..."
echo "  Press Ctrl+C to stop."
echo "============================================================"
echo ""
$PY main.py
