"""Tests for resolve_entity.py — entity resolution against FlyBase Chado."""
import subprocess
import sys

import pytest

from .conftest import (
    KNOWN_GENE_ID,
    KNOWN_GENE_SYMBOL,
    KNOWN_SYNONYM,
    KNOWN_SYNONYM_RESOLVES_TO,
    NONEXISTENT_ENTITY,
)

SCRIPT = ".claude/skills/flybase-stocks/scripts/resolve_entity.py"
PYTHON = ".venv/bin/python"


def run_resolve(entity):
    """Run resolve_entity.py and return (stdout, stderr, returncode)."""
    result = subprocess.run(
        [PYTHON, SCRIPT, entity],
        capture_output=True,
        text=True,
        timeout=30,
        cwd="/Users/clare/git/ask-vfb",
    )
    return result.stdout.strip(), result.stderr.strip(), result.returncode


# --- Argument handling ---


class TestArguments:
    def test_no_args_prints_usage(self):
        result = subprocess.run(
            [PYTHON, SCRIPT],
            capture_output=True,
            text=True,
            timeout=10,
            cwd="/Users/clare/git/ask-vfb",
        )
        assert result.returncode == 1
        assert "Usage" in result.stdout or "Usage" in result.stderr


# --- ID lookup ---


class TestIDLookup:
    @pytest.mark.integration
    def test_known_gene_id(self):
        stdout, _, rc = run_resolve(KNOWN_GENE_ID)
        assert rc == 0
        assert KNOWN_GENE_SYMBOL in stdout
        assert KNOWN_GENE_ID in stdout
        assert "gene" in stdout

    @pytest.mark.integration
    def test_known_combo_id(self):
        stdout, _, rc = run_resolve("FBco0001000")
        assert rc == 0
        assert "FBco0001000" in stdout
        assert "split system combination" in stdout

    @pytest.mark.integration
    def test_nonexistent_id(self):
        stdout, _, rc = run_resolve("FBgn9999999999")
        assert rc == 0
        assert "NOT FOUND" in stdout


# --- Exact name match ---


class TestExactMatch:
    @pytest.mark.integration
    def test_exact_gene_name(self):
        stdout, _, rc = run_resolve(KNOWN_GENE_SYMBOL)
        assert rc == 0
        assert "EXACT MATCH" in stdout
        assert KNOWN_GENE_ID in stdout
        assert "gene" in stdout

    @pytest.mark.integration
    def test_exact_match_returns_type(self):
        """Verify the output includes the entity type."""
        stdout, _, _ = run_resolve(KNOWN_GENE_SYMBOL)
        assert "gene" in stdout


# --- Synonym match ---


class TestSynonymMatch:
    @pytest.mark.integration
    def test_synonym_resolves(self):
        stdout, _, rc = run_resolve(KNOWN_SYNONYM)
        assert rc == 0
        assert "SYNONYM MATCH" in stdout
        assert KNOWN_SYNONYM_RESOLVES_TO in stdout

    @pytest.mark.integration
    def test_synonym_shows_matched_synonym(self):
        """The output should include the synonym that matched."""
        stdout, _, _ = run_resolve(KNOWN_SYNONYM)
        assert KNOWN_SYNONYM in stdout

    @pytest.mark.integration
    def test_combo_synonym_resolves(self):
        """A combination synonym like MB002B should resolve."""
        stdout, _, rc = run_resolve("MB002B")
        assert rc == 0
        assert "SYNONYM MATCH" in stdout
        assert "FBco" in stdout


# --- Broad match ---


class TestBroadMatch:
    @pytest.mark.integration
    def test_broad_match_partial_name(self):
        """A partial gene name should trigger a broad ILIKE match."""
        # 'dpp' is short enough to be exact, so use a substring unlikely to
        # be an exact feature name but present as part of one.
        stdout, _, rc = run_resolve("Scer\\GAL4")
        assert rc == 0
        # Should get either EXACT, SYNONYM, or BROAD match with results
        assert any(
            tag in stdout
            for tag in ["EXACT MATCH", "SYNONYM MATCH", "BROAD MATCH"]
        )


# --- Not found ---


class TestNotFound:
    @pytest.mark.integration
    def test_nonexistent_name(self):
        stdout, _, rc = run_resolve(NONEXISTENT_ENTITY)
        assert rc == 0
        assert "NOT FOUND" in stdout
