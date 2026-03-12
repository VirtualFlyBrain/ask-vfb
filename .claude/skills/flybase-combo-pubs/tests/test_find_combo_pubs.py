"""Tests for find_combo_pubs.py — publication lookup for FlyBase combinations."""
import subprocess

import pytest

from .conftest import (
    CWD,
    KNOWN_COMBO_ID,
    KNOWN_PUB_FBRF,
    PYTHON,
)

SCRIPT = ".claude/skills/flybase-combo-pubs/scripts/find_combo_pubs.py"


def run_find_pubs(fbco_id):
    """Run find_combo_pubs.py and return (stdout, stderr, returncode)."""
    result = subprocess.run(
        [PYTHON, SCRIPT, fbco_id],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=CWD,
    )
    return result.stdout.strip(), result.stderr.strip(), result.returncode


class TestKnownCombo:
    @pytest.mark.integration
    def test_find_pubs_for_known_combo(self):
        stdout, _, rc = run_find_pubs(KNOWN_COMBO_ID)
        assert rc == 0
        assert "Found" in stdout
        assert KNOWN_PUB_FBRF in stdout

    @pytest.mark.integration
    def test_pubs_have_expected_columns(self):
        stdout, _, rc = run_find_pubs(KNOWN_COMBO_ID)
        assert rc == 0
        assert "fbrf" in stdout
        assert "title" in stdout
        assert "doi" in stdout
        assert "pmid" in stdout

    @pytest.mark.integration
    def test_pubs_have_doi(self):
        stdout, _, rc = run_find_pubs(KNOWN_COMBO_ID)
        assert rc == 0
        lines = stdout.strip().split("\n")
        data_lines = [l for l in lines[2:] if l.strip()]
        has_doi = any("10." in line for line in data_lines)
        assert has_doi, "Expected at least one publication with a DOI"


class TestEdgeCases:
    @pytest.mark.integration
    def test_nonexistent_combo(self):
        stdout, _, rc = run_find_pubs("FBco9999999")
        assert rc == 0
        assert "No publications found" in stdout

    def test_missing_argument(self):
        result = subprocess.run(
            [PYTHON, SCRIPT],
            capture_output=True,
            text=True,
            timeout=10,
            cwd=CWD,
        )
        assert result.returncode == 1
        assert "Usage" in result.stdout or "Usage" in result.stderr

    def test_invalid_id_prefix(self):
        result = subprocess.run(
            [PYTHON, SCRIPT, "FBgn0000490"],
            capture_output=True,
            text=True,
            timeout=10,
            cwd=CWD,
        )
        assert result.returncode == 1
        assert "expected FBco" in result.stdout.lower() or "Error" in result.stdout
