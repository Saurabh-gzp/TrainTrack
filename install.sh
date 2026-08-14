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

# 4. Ask for a launch command name
echo ""
printf "  What command name do you want? (e.g. train) [default: traintrack]: "
read CMD_NAME
if [ -z "$CMD_NAME" ]; then
    CMD_NAME="traintrack"
fi
# sanitize (letters, digits, - and _ only)
CMD_NAME=$(echo "$CMD_NAME" | tr -cd 'a-zA-Z0-9_-')
if [ -z "$CMD_NAME" ]; then
    CMD_NAME="traintrack"
fi

# create the launch wrapper
WRAPPER="$INSTALL_DIR/$CMD_NAME"
printf '#!/bin/sh\nexec python3 "%s/traintrack.py" "$@"\n' "$INSTALL_DIR" > "$WRAPPER"
chmod +x "$WRAPPER"
echo "[+] Launch command set: $CMD_NAME"

# 5. Add to PATH (shell rc)
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

# 6. Done
echo ""
echo "=========================================="
echo "  INSTALL COMPLETE!"
echo "=========================================="
echo ""
echo "  Run it in any of these three ways:"
echo ""
echo "  1) Your custom command (recommended):"
echo "     $CMD_NAME"
echo ""
echo "  2) Direct:"
echo "     python3 $INSTALL_DIR/traintrack.py"
echo ""
echo "  3) Full path:"
echo "     $INSTALL_DIR/traintrack.py"
echo ""
echo "  NOTE: open a new terminal so the PATH update takes effect."
echo "=========================================="
echo ""
