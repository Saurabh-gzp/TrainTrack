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
CMD_NAME=""
# When piped via `curl | bash`, stdin is the script itself, so we must read
# from the controlling terminal (/dev/tty) instead. If there is no terminal
# at all (non-interactive), fall back to the default name silently.
if [ -t 0 ]; then
    read -r CMD_NAME
else
    if read -r CMD_NAME < /dev/tty 2>/dev/null; then
        :
    fi
fi
if [ -z "$CMD_NAME" ]; then
    CMD_NAME="traintrack"
fi
# sanitize (letters, digits, - and _ only)
CMD_NAME=$(printf '%s' "$CMD_NAME" | tr -cd 'a-zA-Z0-9_-')
if [ -z "$CMD_NAME" ]; then
    CMD_NAME="traintrack"
fi

# 5. Install the launch command into a directory that is ALREADY in PATH
#    so it works immediately (no new terminal needed).
installed_bin=""
if [ -n "$PREFIX" ] && [ -d "$PREFIX/bin" ]; then
    # Termux: $PREFIX/bin is always in PATH and writable by the user
    BIN_DIR="$PREFIX/bin"
    installed_bin="yes"
elif [ -d "$HOME/.local/bin" ]; then
    BIN_DIR="$HOME/.local/bin"
    installed_bin="yes"
elif [ -d "$HOME/bin" ]; then
    BIN_DIR="$HOME/bin"
    installed_bin="yes"
fi

# Always create the wrapper in INSTALL_DIR (fallback + full-path run)
WRAPPER="$INSTALL_DIR/$CMD_NAME"
printf '#!/bin/sh\nexec python3 "%s/traintrack.py" "$@"\n' "$INSTALL_DIR" > "$WRAPPER"
chmod +x "$WRAPPER"

# Create the actual command (symlink into a PATH directory if possible)
if [ "$installed_bin" = "yes" ]; then
    ln -sf "$WRAPPER" "$BIN_DIR/$CMD_NAME"
    echo "[+] Command installed: $CMD_NAME  (in $BIN_DIR)"
    echo "[+] It works immediately — no new terminal needed."
else
    echo "[+] Launch wrapper created: $WRAPPER"
fi

# 6. Add INSTALL_DIR to PATH (shell rc) as a fallback
add_path() {
    RC="$1"
    if [ -f "$RC" ]; then
        if ! grep -q "traintrack" "$RC" 2>/dev/null; then
            echo "" >> "$RC"
            echo "# TrainTrack" >> "$RC"
            echo "export PATH=\"\$PATH:$INSTALL_DIR\"" >> "$RC"
        fi
    fi
}
add_path "$HOME/.bashrc"
add_path "$HOME/.zshrc"
add_path "$HOME/.profile"

# 7. Make it available in the CURRENT session too
if [ "$installed_bin" = "yes" ]; then
    export PATH="$BIN_DIR:$PATH"
fi

# 8. Done
echo ""
echo "=========================================="
echo "  INSTALL COMPLETE!"
echo "=========================================="
echo ""
echo "  Run it in any of these three ways:"
echo ""
echo "  1) Your command:"
echo "     $CMD_NAME"
echo ""
echo "  2) Direct:"
echo "     python3 $INSTALL_DIR/traintrack.py"
echo ""
echo "  3) Full path:"
echo "     $INSTALL_DIR/traintrack.py"
echo ""
echo "=========================================="
echo ""
echo "  *** IMPORTANT: RESTART TERMUX ***"
echo ""
echo "  If the '$CMD_NAME' command does not work yet,"
echo "  you MUST fully restart Termux:"
echo ""
echo "    -> Close the Termux app completely (swipe it away)"
echo "    -> Then open it again"
echo ""
echo "  After restarting, the '$CMD_NAME' command will work."
echo ""
echo "=========================================="
echo ""
