"""Shared fixtures for flybase-combo-pubs tests."""
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
KNOWN_COMBO_ID = "FBco0000052"
KNOWN_COMBO_SYNONYM = "MB002B"
KNOWN_PUB_FBRF = "FBrf0227179"  # Aso et al., 2014

NONEXISTENT_COMBO = "NONEXISTENT_COMBO_XYZ"

CWD = "/Users/clare/git/ask-vfb"
PYTHON = ".venv/bin/python"


@pytest.fixture(scope="session")
def db_conn():
    """Session-scoped connection to the FlyBase public Chado database."""
    conn = chado_connect(connect_timeout=30)
    yield conn
    conn.close()
