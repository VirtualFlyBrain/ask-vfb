"""Shared fixtures for flybase-stocks tests."""
import pytest
import psycopg

# Well-known stable entities for integration tests
KNOWN_GENE_SYMBOL = "dpp"
KNOWN_GENE_ID = "FBgn0000490"

KNOWN_GENE_SYMBOL_2 = "w"
KNOWN_GENE_ID_2 = "FBgn0003996"

# CG9885 is a known synonym for dpp
KNOWN_SYNONYM = "CG9885"
KNOWN_SYNONYM_RESOLVES_TO = "dpp"

NONEXISTENT_ENTITY = "xyzzy_nonexistent_gene_99999"


@pytest.fixture(scope="session")
def db_conn():
    """Session-scoped connection to the FlyBase public Chado database."""
    conn = psycopg.connect(
        host="chado.flybase.org",
        dbname="flybase",
        user="flybase",
        password="flybase",
        connect_timeout=15,
        options="-c statement_timeout=120000",
    )
    yield conn
    conn.close()
