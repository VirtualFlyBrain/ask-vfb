#!/usr/bin/env bash
# One-off setup for the vfb-video skill. Safe to re-run. Does NOT end with `exit`.
set -u
cd "$(dirname "$0")/../../../.." 2>/dev/null || true
PY=".venv/bin/python"; [ -x "$PY" ] || PY="python3"
echo "Python: $PY"
command -v ffmpeg >/dev/null || echo "MISSING: ffmpeg (macOS: brew install ffmpeg | Ubuntu: sudo apt install ffmpeg)"
"$PY" -m pip install --quiet playwright && "$PY" -m playwright install chromium
CACHE="${XDG_CACHE_HOME:-$HOME/.cache}/vfb-video"; mkdir -p "$CACHE"
if [ ! -s "$CACHE/three.module.min.js" ]; then
  curl -fsSL -o "$CACHE/three.module.min.js" https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.module.min.js && echo "three.js cached"
fi
echo "setup done"
