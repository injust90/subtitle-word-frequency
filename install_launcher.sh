#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_BIN="${PYTHON_BIN:-$(command -v python3)}"
ICON_PATH="$SCRIPT_DIR/icon_001.png"
APP_PATH="$SCRIPT_DIR/word_frequency.py"
DESKTOP_DIR="$HOME/.local/share/applications"
DESKTOP_FILE="$DESKTOP_DIR/WordFrequency.desktop"

mkdir -p "$DESKTOP_DIR"

cat > "$DESKTOP_FILE" <<EOF
[Desktop Entry]
Type=Application
Name=Word Frequency
Comment=Compute word frequencies from subtitle files
Exec=$PYTHON_BIN $APP_PATH
Terminal=false
Icon=$ICON_PATH
Categories=Utility;
EOF

chmod +x "$DESKTOP_FILE"

echo "Installed launcher to: $DESKTOP_FILE"
