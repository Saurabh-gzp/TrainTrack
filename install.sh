#!/bin/sh
# TrainTrack — one-command installer
# Works on: Linux, macOS, Termux, WSL
set -e

REPO="https://raw.githubusercontent.com/Saurabh-gzp/TrainTrack/main"
INSTALL_DIR="${HOME}/.traintrack"

echo ""
echo "=========================================="
echo "  TrainTrack — Indian Railways CLI"
echo "  Installer"
echo "=========================================="
echo ""

# 1. Check python3
if ! command -v python3 >/dev/null 2>&1; then
    echo "[!] python3 not found. Install it with:"
    echo "    Linux (Debian/Ubuntu): sudo apt install python3"
    echo "    Termux:                pkg install python"
    echo "    macOS:                 brew install python3"
    exit 1
fi
echo "[+] python3: $(python3 --version)"

# 2. Check curl or wget
if command -v curl >/dev/null 2>&1; then
    FETCH="curl -fsSL"
elif command -v wget >/dev/null 2>&1; then
    FETCH="wget -qO-"
else
    echo "[!] curl or wget is required. Termux: pkg install curl"
    exit 1
fi

# 3. Download script
echo "[+] Downloading traintrack.py..."
mkdir -p "$INSTALL_DIR"
$FETCH "$REPO/traintrack.py" > "$INSTALL_DIR/traintrack.py"
chmod +x "$INSTALL_DIR/traintrack.py"

# 4. Add to PATH (shell rc)
add_path() {
    RC="$1"
    if [ -f "$RC" ]; then
        if ! grep -q "traintrack" "$RC" 2>/dev/null; then
            echo "" >> "$RC"
            echo "# TrainTrack" >> "$RC"
            echo "export PATH=\"\$PATH:$INSTALL_DIR\"" >> "$RC"
            echo "[+] PATH added to $RC"
        fi
    fi
}

add_path "$HOME/.bashrc"
add_path "$HOME/.zshrc"
add_path "$HOME/.profile"

# 5. Done
echo ""
echo "=========================================="
echo "  INSTALL COMPLETE!"
echo "=========================================="
echo ""
echo "  Run it in either of two ways:"
echo ""
echo "  1) Direct (recommended):"
echo "     python3 $INSTALL_DIR/traintrack.py"
echo ""
echo "  2) Command (after opening a new terminal):"
echo "     traintrack.py"
echo ""
echo "  NOTE: open a new terminal so the PATH update takes effect."
echo "=========================================="
echo ""
