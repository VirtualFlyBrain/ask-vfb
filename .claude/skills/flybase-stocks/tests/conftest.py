"""Shared fixtures for flybase-stocks tests."""
import pytest
import psycopg


# VFB's own copy of FlyBase Chado first (chado.flybase.virtualflybrain.org:443, Postgres 17 direct SSL, which
# psycopg[binary] supports), then FlyBase's public server. FB_CHADO_HOST overrides: comma-separated host or host:port.
_CHADO_HOSTS = "chado.flybase.virtualflybrain.org:443,chado.flybase.org"


def chado_connect(**kwargs):
    """psycopg connection to the first reachable Chado server; kwargs as for psycopg.connect."""
    import os
    import sys
    hosts = [h.strip() for h in (os.environ.get("FB_CHADO_HOST") or _CHADO_HOSTS).split(",") if h.strip()]
    for i, entry in enumerate(hosts):
        host, _, port = entry.partition(":")
        args = dict(kwargs, host=host, dbname="flybase", user="flybase", password="flybase")
        if port:
            args["port"] = int(port)
        if port == "443":
            args.update(sslmode="require", sslnegotiation="direct")
        try:
            return psycopg.connect(**args)
        except psycopg.Error as e:
            if i == len(hosts) - 1:
                raise
            print("Chado at %s unavailable (%s); trying %s" % (entry, str(e).strip().splitlines()[0] if str(e).strip() else type(e).__name__, hosts[i + 1]), file=sys.stderr)

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
    conn = chado_connect(connect_timeout=15, options="-c statement_timeout=120000")
    yield conn
    conn.close()
