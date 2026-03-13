"""Tests for resolve_combination.py — combination resolution against FlyBase Chado."""
import subprocess

import pytest

from .conftest import (
    CWD,
    KNOWN_COMBO_ID,
    KNOWN_COMBO_SYNONYM,
    NONEXISTENT_COMBO,
    PYTHON,
)

SCRIPT = ".claude/skills/flybase-combo-pubs/scripts/resolve_combination.py"


def run_resolve(entity):
    """Run resolve_combination.py and return (stdout, stderr, returncode)."""
    result = subprocess.run(
        [PYTHON, SCRIPT, entity],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=CWD,
    )
    return result.stdout.strip(), result.stderr.strip(), result.returncode


class TestIDLookup:
    @pytest.mark.integration
    def test_known_combo_id(self):
        stdout, _, rc = run_resolve(KNOWN_COMBO_ID)
        assert rc == 0
        assert "EXACT MATCH" in stdout
        assert KNOWN_COMBO_ID in stdout


class TestSynonymMatch:
    @pytest.mark.integration
    def test_synonym_resolves(self):
        stdout, _, rc = run_resolve(KNOWN_COMBO_SYNONYM)
        assert rc == 0
        assert "SYNONYM MATCH" in stdout
        assert KNOWN_COMBO_ID in stdout

    @pytest.mark.integration
    def test_synonym_shows_matched_synonym(self):
        stdout, _, _ = run_resolve(KNOWN_COMBO_SYNONYM)
        assert KNOWN_COMBO_SYNONYM in stdout


class TestBroadMatch:
    @pytest.mark.integration
    def test_broad_match_partial_name(self):
        stdout, _, rc = run_resolve("R14C08")
        assert rc == 0
        assert any(
            tag in stdout
            for tag in ["EXACT MATCH", "SYNONYM MATCH", "BROAD MATCH"]
        )
        assert "FBco" in stdout


class TestNotFound:
    @pytest.mark.integration
    def test_nonexistent_name(self):
        stdout, _, rc = run_resolve(NONEXISTENT_COMBO)
        assert rc == 0
        assert "NOT FOUND" in stdout


class TestArguments:
    def test_no_args_prints_usage(self):
        result = subprocess.run(
            [PYTHON, SCRIPT],
            capture_output=True,
            text=True,
            timeout=10,
            cwd=CWD,
        )
        assert result.returncode == 1
        assert "Usage" in result.stdout or "Usage" in result.stderr
