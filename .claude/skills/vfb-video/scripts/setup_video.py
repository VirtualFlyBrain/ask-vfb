#!/usr/bin/env python3
"""One-off setup for the vfb-video skill (safe to re-run).

Installs Playwright and its Chromium browser into the Python you run this with
(use the repo's .venv: .venv/bin/python .claude/skills/vfb-video/scripts/setup_video.py)
and checks that ffmpeg is available.
"""
import shutil, subprocess, sys

def run(cmd):
    print("+", " ".join(cmd), flush=True)
    return subprocess.call(cmd)

def main():
    if sys.version_info < (3, 9):
        print("Python 3.9 or newer is required."); return 1
    if run([sys.executable, "-m", "pip", "install", "--quiet", "playwright"]) != 0:
        print("Could not install playwright (pip failed)."); return 1
    if run([sys.executable, "-m", "playwright", "install", "chromium"]) != 0:
        print("Could not download Chromium for Playwright."); return 1
    if shutil.which("ffmpeg") is None:
        print("\nMISSING: ffmpeg. Install it, then you are ready:\n"
              "  macOS:   brew install ffmpeg\n  Ubuntu:  sudo apt install ffmpeg\n"
              "  Windows: winget install Gyan.FFmpeg")
        return 1
    print("\nSetup complete: Playwright, Chromium and ffmpeg are ready.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
