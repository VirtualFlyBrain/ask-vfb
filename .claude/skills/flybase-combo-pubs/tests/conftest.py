"""Shared fixtures for flybase-combo-pubs tests."""
import pytest
import psycopg

# Well-known stable entities for integration tests
KNOWN_COMBO_ID = "FBco0000052"
KNOWN_COMBO_SYNONYM = "MB002B"
KNOWN_PUB_FBRF = "FBrf0227179"  # Aso et al., 2014

NONEXISTENT_COMBO = "NONEXISTENT_COMBO_XYZ"

CWD = "/Users/clare/git/ask-vfb"
PYTHON = ".venv/bin/python"


@pytest.fixture(scope="session")
def db_conn():
    """Session-scoped connection to the FlyBase public Chado database."""
    conn = psycopg.connect(
        host="chado.flybase.org",
        dbname="flybase",
        user="flybase",
        password="flybase",
        connect_timeout=30,
    )
    yield conn
    conn.close()
