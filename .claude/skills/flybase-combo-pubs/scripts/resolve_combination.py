#!/usr/bin/env python3
"""Resolve a FlyBase combination (FBco) by ID, name, or synonym.

Usage: resolve_combination.py <name_or_id>

Returns tab-separated rows with columns:
    name, uniquename, matched_synonym (if via synonym)

Output prefixes:
    EXACT MATCH  — matched on feature.name
    SYNONYM MATCH — matched on synonym.name
    BROAD MATCH  — matched via ILIKE on feature.name
    NOT FOUND    — no match
"""
import sys

import pandas as pd
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

def connect():
    return chado_connect(connect_timeout=30)


FEATURE_TYPE = "split system combination"


def resolve_by_id(cur, fbco_id):
    """Resolve by FBco uniquename."""
    cur.execute(
        """
        SELECT f.name, f.uniquename
        FROM feature f
        JOIN cvterm c ON f.type_id = c.cvterm_id
        WHERE f.uniquename = %(uid)s
          AND c.name = %(ftype)s
          AND f.is_obsolete = false
        """,
        {"uid": fbco_id, "ftype": FEATURE_TYPE},
    )
    rows = cur.fetchall()
    if rows:
        print("EXACT MATCH")
        df = pd.DataFrame(rows, columns=["name", "uniquename"])
        print(df.to_csv(sep="\t", index=False))
    else:
        print("NOT FOUND")


def resolve_by_name(cur, name):
    """Try exact name, then synonym, then broad ILIKE."""
    # 1. Exact match on feature.name
    cur.execute(
        """
        SELECT f.name, f.uniquename
        FROM feature f
        JOIN cvterm c ON f.type_id = c.cvterm_id
        WHERE f.name = %(name)s
          AND c.name = %(ftype)s
          AND f.is_obsolete = false
        """,
        {"name": name, "ftype": FEATURE_TYPE},
    )
    rows = cur.fetchall()
    if rows:
        print("EXACT MATCH")
        df = pd.DataFrame(rows, columns=["name", "uniquename"])
        print(df.to_csv(sep="\t", index=False))
        return

    # 2. Synonym match
    cur.execute(
        """
        SELECT DISTINCT f.name, f.uniquename, s.name AS matched_synonym
        FROM feature f
        JOIN cvterm c ON f.type_id = c.cvterm_id
        JOIN feature_synonym fs ON f.feature_id = fs.feature_id
        JOIN synonym s ON fs.synonym_id = s.synonym_id
        WHERE s.name = %(name)s
          AND c.name = %(ftype)s
          AND f.is_obsolete = false
        """,
        {"name": name, "ftype": FEATURE_TYPE},
    )
    rows = cur.fetchall()
    if rows:
        print("SYNONYM MATCH")
        df = pd.DataFrame(rows, columns=["name", "uniquename", "matched_synonym"])
        print(df.to_csv(sep="\t", index=False))
        return

    # 3. Broad ILIKE on name and synonyms
    pattern = f"%{name}%"
    cur.execute(
        """
        SELECT DISTINCT f.name, f.uniquename
        FROM feature f
        JOIN cvterm c ON f.type_id = c.cvterm_id
        WHERE (f.name ILIKE %(pat)s)
          AND c.name = %(ftype)s
          AND f.is_obsolete = false

        UNION

        SELECT DISTINCT f.name, f.uniquename
        FROM feature f
        JOIN cvterm c ON f.type_id = c.cvterm_id
        JOIN feature_synonym fs ON f.feature_id = fs.feature_id
        JOIN synonym s ON fs.synonym_id = s.synonym_id
        WHERE s.name ILIKE %(pat)s
          AND c.name = %(ftype)s
          AND f.is_obsolete = false

        ORDER BY uniquename
        LIMIT 20
        """,
        {"pat": pattern, "ftype": FEATURE_TYPE},
    )
    rows = cur.fetchall()
    if rows:
        print("BROAD MATCH")
        df = pd.DataFrame(rows, columns=["name", "uniquename"])
        print(df.to_csv(sep="\t", index=False))
        return

    print("NOT FOUND")


def main():
    if len(sys.argv) < 2:
        print("Usage: resolve_combination.py <name_or_id>")
        sys.exit(1)

    query = " ".join(sys.argv[1:]).strip()
    conn = connect()
    cur = conn.cursor()

    import re

    if re.match(r"FBco\d+", query):
        resolve_by_id(cur, query)
    else:
        resolve_by_name(cur, query)

    conn.close()


if __name__ == "__main__":
    main()
