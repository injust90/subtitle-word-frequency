#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
PYTHON="${PYTHON:-$SCRIPT_DIR/.venv/bin/python}"
APP="$SCRIPT_DIR/word_frequency.py"

set +e
"$PYTHON" "$APP" "$@"
status=$?
echo
read -r -p "Done. Press Enter to close..." _
exit $status
