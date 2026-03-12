"""Tests for list_datasets.py — available connectome datasets from VFB."""
import subprocess

import pytest

from .conftest import CWD, PYTHON, SCRIPT_DIR

SCRIPT = f"{SCRIPT_DIR}/list_datasets.py"


def run_list_datasets():
    """Run list_datasets.py and return (stdout, stderr, returncode)."""
    result = subprocess.run(
        [PYTHON, SCRIPT],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=CWD,
    )
    return result.stdout.strip(), result.stderr.strip(), result.returncode


class TestListDatasets:
    @pytest.mark.integration
    def test_runs_successfully(self):
        _, _, rc = run_list_datasets()
        assert rc == 0

    @pytest.mark.integration
    def test_has_header(self):
        stdout, _, _ = run_list_datasets()
        assert "Label" in stdout
        assert "Symbol" in stdout

    @pytest.mark.integration
    def test_returns_datasets(self):
        """Should return at least one dataset."""
        stdout, _, _ = run_list_datasets()
        # Lines after header and separator
        data_lines = [
            l for l in stdout.split("\n")
            if l.strip() and "Label" not in l and "---" not in l
        ]
        assert len(data_lines) > 0

    @pytest.mark.integration
    def test_hemibrain_present(self):
        """Hemibrain is a stable, well-known dataset that should always exist."""
        stdout, _, _ = run_list_datasets()
        assert "hb" in stdout

    @pytest.mark.integration
    def test_every_row_has_symbol(self):
        """Each dataset row should have a non-empty symbol."""
        stdout, _, _ = run_list_datasets()
        data_lines = [
            l for l in stdout.split("\n")
            if l.strip() and "Label" not in l and "---" not in l
        ]
        for line in data_lines:
            # Symbol is the last whitespace-separated token
            parts = line.split()
            assert len(parts) >= 2, f"Row appears to lack a symbol: {line!r}"
