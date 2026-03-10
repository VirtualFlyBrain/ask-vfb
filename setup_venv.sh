#!/usr/bin/env bash
set -e

# Find highest available Python version between 3.9 and 3.13
PYTHON=""
for version in 3.13 3.12 3.11 3.10 3.9; do
    if command -v "python${version}" &>/dev/null; then
        PYTHON="python${version}"
        break
    fi
done

if [ -z "$PYTHON" ]; then
    # Fallback: check if generic python3 meets version requirement
    if command -v python3 &>/dev/null; then
        PY3_VER=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
        case "$PY3_VER" in
            3.9|3.10|3.11|3.12|3.13) PYTHON="python3" ;;
        esac
    fi
fi

if [ -z "$PYTHON" ]; then
    echo "Error: No Python 3.9–3.13 found. Please install a supported version."
    exit 1
fi

echo "Using $($PYTHON --version)"

VENV_DIR="${1:-.venv}"

$PYTHON -m venv "$VENV_DIR"

# Activate and install dependencies
source "$VENV_DIR/bin/activate"

pip install --upgrade pip
pip install -r "$(dirname "$0")/requirements.txt"

echo "Done. Activate with: source $VENV_DIR/bin/activate"
