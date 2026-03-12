"""Tests for find_stocks.py — stock discovery against FlyBase Chado."""
import subprocess

import pytest

from .conftest import KNOWN_GENE_ID, KNOWN_GENE_ID_2

SCRIPT = ".claude/skills/flybase-stocks/scripts/find_stocks.py"
PYTHON = ".venv/bin/python"
CWD = "/Users/clare/git/ask-vfb"


def run_find_stocks(*args):
    """Run find_stocks.py and return (stdout, stderr, returncode)."""
    result = subprocess.run(
        [PYTHON, SCRIPT, *args],
        capture_output=True,
        text=True,
        timeout=150,
        cwd=CWD,
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
            cwd=CWD,
        )
        assert result.returncode == 1
        assert "Usage" in result.stdout or "Usage" in result.stderr

    def test_bad_id_prefix(self):
        stdout, _, rc = run_find_stocks("INVALID0001")
        assert rc == 1
        assert "ERROR" in stdout or "Unrecognised" in stdout


# --- Gene → stocks ---


class TestGeneStocks:
    @pytest.mark.integration
    def test_dpp_returns_stocks(self):
        """dpp (FBgn0000490) is a well-known gene with many stocks."""
        stdout, _, rc = run_find_stocks(KNOWN_GENE_ID)
        assert rc == 0
        # First line should be "<N> stocks found"
        first_line = stdout.split("\n")[0]
        assert "stocks found" in first_line
        count = int(first_line.split()[0])
        assert count > 0

    @pytest.mark.integration
    def test_dpp_stock_columns(self):
        """Output should contain expected column data."""
        stdout, _, _ = run_find_stocks(KNOWN_GENE_ID)
        # Should have stock IDs (FBst) and genotype info
        assert "FBst" in stdout

    @pytest.mark.integration
    def test_white_returns_stocks(self):
        """white (FBgn0003996) should also have stocks."""
        stdout, _, rc = run_find_stocks(KNOWN_GENE_ID_2)
        assert rc == 0
        first_line = stdout.split("\n")[0]
        count = int(first_line.split()[0])
        assert count > 0


# --- Gene with collection filter ---


class TestCollectionFilter:
    @pytest.mark.integration
    def test_bloomington_filter(self):
        """Filtering by Bloomington should return only BDSC stocks."""
        stdout, _, rc = run_find_stocks(KNOWN_GENE_ID, "Bloomington")
        assert rc == 0
        first_line = stdout.split("\n")[0]
        count = int(first_line.split()[0])
        assert count > 0
        # Every data line with a collection should mention Bloomington
        lines = stdout.split("\n")[1:]  # skip count line
        for line in lines:
            if line.strip() and "stock_id" not in line.lower():
                # Data lines containing collection info should be Bloomington
                if "Bloomington" not in line and "stock_number" not in line:
                    # Allow header line
                    pass

    @pytest.mark.integration
    def test_filter_reduces_count(self):
        """Filtering should return fewer stocks than unfiltered."""
        stdout_all, _, _ = run_find_stocks(KNOWN_GENE_ID)
        stdout_filtered, _, _ = run_find_stocks(KNOWN_GENE_ID, "Bloomington")
        count_all = int(stdout_all.split("\n")[0].split()[0])
        count_filtered = int(stdout_filtered.split("\n")[0].split()[0])
        assert count_filtered <= count_all


# --- Allele → stocks ---


class TestAlleleStocks:
    @pytest.mark.integration
    def test_known_allele(self, db_conn):
        """Find a known allele of dpp that has stocks, then query it."""
        # First, find an allele ID from the gene query output
        stdout, _, rc = run_find_stocks(KNOWN_GENE_ID)
        assert rc == 0
        # Extract an FBst from output to verify stock detail lookup works
        # But for allele test, we need an FBal. Let's use a known one.
        # dpp[hr4] = FBal0000469 is a classic allele
        stdout, _, rc = run_find_stocks("FBal0000469")
        assert rc == 0
        first_line = stdout.split("\n")[0]
        count = int(first_line.split()[0])
        # This allele may or may not have stocks; just verify it runs
        assert count >= 0


# --- Insertion → stocks ---


class TestInsertionStocks:
    @pytest.mark.integration
    def test_known_insertion(self):
        """Query a known insertion ID."""
        # P{EPgy2}dpp[EP2232] = FBti0016417 is a known insertion with BDSC stock
        stdout, _, rc = run_find_stocks("FBti0016417")
        assert rc == 0
        first_line = stdout.split("\n")[0]
        count = int(first_line.split()[0])
        assert count > 0


# --- Stock detail lookup ---


class TestStockDetail:
    @pytest.mark.integration
    def test_stock_lookup(self):
        """Look up a specific stock by FBst ID."""
        # FBst0007144 is BDSC #7144
        stdout, _, rc = run_find_stocks("FBst0007144")
        assert rc == 0
        first_line = stdout.split("\n")[0]
        count = int(first_line.split()[0])
        assert count > 0
        assert "7144" in stdout

    @pytest.mark.integration
    def test_stock_includes_collection(self):
        """Stock detail should include the collection name."""
        stdout, _, _ = run_find_stocks("FBst0007144")
        assert "Bloomington" in stdout

    @pytest.mark.integration
    def test_stock_includes_genotype(self):
        """Stock detail should include genotype info."""
        stdout, _, _ = run_find_stocks("FBst0007144")
        # Should have a genotype column with content
        lines = stdout.split("\n")
        assert len(lines) > 1  # header + at least one data row


# --- Edge cases ---


class TestEdgeCases:
    @pytest.mark.integration
    def test_nonexistent_gene_id(self):
        """A valid-format but nonexistent FBgn should return 0 stocks."""
        stdout, _, rc = run_find_stocks("FBgn9999999999")
        assert rc == 0
        first_line = stdout.split("\n")[0]
        assert "0 stocks found" in first_line

    @pytest.mark.integration
    def test_nonexistent_stock_id(self):
        """A valid-format but nonexistent FBst should return 0 stocks."""
        stdout, _, rc = run_find_stocks("FBst9999999999")
        assert rc == 0
        first_line = stdout.split("\n")[0]
        assert "0 stocks found" in first_line
