"""Resolve a FlyBase entity name or ID via the Chado database."""
import sys
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

import pandas as pd


def run_query(conn, sql, params):
    """Execute a query and return a DataFrame."""
    with conn.cursor() as cur:
        cur.execute(sql, params)
        rows = cur.fetchall()
        if not rows:
            return pd.DataFrame()
        columns = [desc[0] for desc in cur.description]
        return pd.DataFrame(rows, columns=columns)


def main():
    entity = sys.argv[1] if len(sys.argv) > 1 else None
    if not entity:
        print("Usage: resolve_entity.py <name_or_id>")
        sys.exit(1)

    conn = chado_connect(connect_timeout=10)

    try:
        if entity.startswith(("FBgn", "FBal", "FBti", "FBst", "FBco")):
            df = run_query(conn, """
                SELECT f.name, f.uniquename, c.name AS type
                FROM feature f
                JOIN cvterm c ON f.type_id = c.cvterm_id
                WHERE f.uniquename = %(id)s AND f.is_obsolete = false
            """, {"id": entity})
            print(df.to_string(index=False) if len(df) > 0 else "NOT FOUND")
            return

        # Try exact match on feature.name
        df = run_query(conn, """
            SELECT DISTINCT f.name, f.uniquename, c.name AS type
            FROM feature f
            JOIN cvterm c ON f.type_id = c.cvterm_id
            WHERE f.is_obsolete = false
              AND c.name IN ('gene', 'allele', 'transposable_element_insertion_site',
                             'chromosome_structure_variation', 'split system combination')
              AND f.name = %(name)s
            ORDER BY c.name, f.name
            LIMIT 20
        """, {"name": entity})

        if len(df) > 0:
            print("EXACT MATCH")
            print(df.to_string(index=False))
            return

        # Fall back to synonym search
        df = run_query(conn, """
            SELECT DISTINCT f.name, f.uniquename, c.name AS type,
                   syn.name AS matched_synonym
            FROM feature f
            JOIN cvterm c ON f.type_id = c.cvterm_id
            JOIN feature_synonym fs ON f.feature_id = fs.feature_id
            JOIN synonym syn ON fs.synonym_id = syn.synonym_id
            WHERE f.is_obsolete = false
              AND c.name IN ('gene', 'allele',
                             'transposable_element_insertion_site',
                             'chromosome_structure_variation',
                             'split system combination')
              AND syn.name ILIKE %(name)s
            ORDER BY c.name, f.name
            LIMIT 20
        """, {"name": entity})

        if len(df) > 0:
            print("SYNONYM MATCH")
            print(df.to_string(index=False))
            return

        # Broad ILIKE search
        df = run_query(conn, """
            SELECT DISTINCT f.name, f.uniquename, c.name AS type
            FROM feature f
            JOIN cvterm c ON f.type_id = c.cvterm_id
            WHERE f.is_obsolete = false
              AND c.name IN ('gene', 'allele',
                             'transposable_element_insertion_site',
                             'chromosome_structure_variation',
                             'split system combination')
              AND (f.name ILIKE %(pattern)s)
            ORDER BY c.name, f.name
            LIMIT 20
        """, {"pattern": "%" + entity + "%"})

        if len(df) > 0:
            print("BROAD MATCH")
            print(df.to_string(index=False))
            return

        print("NOT FOUND")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
