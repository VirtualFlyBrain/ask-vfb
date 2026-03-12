"""Shared fixtures and constants for vfb-connectivity tests."""
import pytest

SCRIPT_DIR = ".claude/skills/vfb-connectivity/scripts"
PYTHON = ".venv/bin/python"
CWD = "/Users/clare/git/ask-vfb"

# Giant fiber → PSI is a textbook Drosophila connection, stable across datasets
KNOWN_UPSTREAM = "giant fiber neuron"
KNOWN_DOWNSTREAM = "peripherally synapsing interneuron"
