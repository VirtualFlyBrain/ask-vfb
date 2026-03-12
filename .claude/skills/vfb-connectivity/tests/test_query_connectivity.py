"""Tests for query_connectivity.py — neuron connectivity queries against VFB."""
import subprocess
import re

import pytest

from .conftest import CWD, PYTHON, SCRIPT_DIR, KNOWN_UPSTREAM, KNOWN_DOWNSTREAM

SCRIPT = f"{SCRIPT_DIR}/query_connectivity.py"


def run_query(*args):
    """Run query_connectivity.py and return (stdout, stderr, returncode)."""
    result = subprocess.run(
        [PYTHON, SCRIPT, *args],
        capture_output=True,
        text=True,
        timeout=300,
        cwd=CWD,
    )
    return result.stdout.strip(), result.stderr.strip(), result.returncode


def parse_count(stdout):
    """Extract the connection count from output (may not be the first line)."""
    m = re.search(r"(\d+) connections found", stdout)
    return int(m.group(1)) if m else 0


# --- Argument handling ---


class TestArguments:
    def test_no_args_prints_error(self):
        stdout, _, rc = run_query()
        assert rc == 1
        assert "ERROR" in stdout

    def test_help(self):
        result = subprocess.run(
            [PYTHON, SCRIPT, "--help"],
            capture_output=True,
            text=True,
            timeout=30,
            cwd=CWD,
        )
        assert result.returncode == 0
        assert "--upstream" in result.stdout
        assert "--downstream" in result.stdout


# --- Integration: known connection ---


class TestKnownConnection:
    @pytest.mark.integration
    def test_both_types_subset_of_either_alone(self):
        """Giant fiber → PSI is a classic connection. All three query modes
        (both, upstream-only, downstream-only) should return results, and
        specifying both should return a subset of either alone."""
        stdout_both, _, rc_both = run_query(
            "--upstream", KNOWN_UPSTREAM,
            "--downstream", KNOWN_DOWNSTREAM,
        )
        stdout_up, _, rc_up = run_query("--upstream", KNOWN_UPSTREAM)
        stdout_down, _, rc_down = run_query("--downstream", KNOWN_DOWNSTREAM)

        assert rc_both == 0
        assert rc_up == 0
        assert rc_down == 0

        count_both = parse_count(stdout_both)
        count_up = parse_count(stdout_up)
        count_down = parse_count(stdout_down)

        assert count_both > 0
        assert count_both <= count_up
        assert count_both <= count_down


# --- Group by class ---


class TestGroupByClass:
    @pytest.mark.integration
    def test_group_by_class(self):
        """--group-by-class should return results with class-level columns."""
        stdout, _, rc = run_query(
            "--upstream", KNOWN_UPSTREAM,
            "--downstream", KNOWN_DOWNSTREAM,
            "--group-by-class",
        )
        assert rc == 0
        assert "connections found" in stdout
        # Class-aggregated output has these columns
        assert "upstream_class" in stdout
        assert "downstream_class" in stdout


# --- Weight filtering ---


class TestWeightFiltering:
    @pytest.mark.integration
    def test_higher_weight_fewer_results(self):
        """A higher weight threshold should return fewer or equal results."""
        stdout_low, _, _ = run_query(
            "--upstream", KNOWN_UPSTREAM,
            "--downstream", KNOWN_DOWNSTREAM,
            "--weight", "1",
        )
        stdout_high, _, _ = run_query(
            "--upstream", KNOWN_UPSTREAM,
            "--downstream", KNOWN_DOWNSTREAM,
            "--weight", "50",
        )
        count_low = parse_count(stdout_low)
        count_high = parse_count(stdout_high)
        assert count_low >= count_high


# --- Exclude DBs ---


class TestExcludeDbs:
    @pytest.mark.integration
    def test_exclude_all_returns_no_results(self):
        """Excluding every dataset should return no connections gracefully."""
        # First get the full dataset symbol list
        list_result = subprocess.run(
            [PYTHON, f"{SCRIPT_DIR}/list_datasets.py"],
            capture_output=True,
            text=True,
            timeout=60,
            cwd=CWD,
        )
        # Parse symbols from output
        symbols = []
        for line in list_result.stdout.strip().split("\n"):
            if line.strip() and "Label" not in line and "---" not in line:
                parts = line.split()
                if parts:
                    symbols.append(parts[-1])
        assert len(symbols) > 0, "Could not parse dataset symbols"

        stdout, _, rc = run_query(
            "--upstream", KNOWN_UPSTREAM,
            "--downstream", KNOWN_DOWNSTREAM,
            "--exclude-dbs", *symbols,
        )
        assert rc == 0
        assert "No connections found" in stdout


# --- Nonexistent neuron type ---


class TestEdgeCases:
    @pytest.mark.integration
    def test_nonexistent_type_exits_with_error(self):
        """A made-up neuron type should be caught and reported as an error,
        not silently ignored."""
        stdout, _, rc = run_query(
            "--upstream", "xyzzy_nonexistent_neuron_type_99999",
            "--downstream", KNOWN_DOWNSTREAM,
        )
        assert rc == 1
        assert "ERROR" in stdout
        assert "did not recognise" in stdout
