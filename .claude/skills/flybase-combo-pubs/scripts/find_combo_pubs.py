#!/usr/bin/env python3
"""Find publications linked to a FlyBase combination (FBco).

Usage: find_combo_pubs.py <FBco_ID>

Returns tab-separated rows with columns:
    fbrf, title, year, miniref, pub_type, doi, pmid, pmcid
"""
import sys

import pandas as pd
import psycopg


def connect():
    return psycopg.connect(
        host="chado.flybase.org",
        dbname="flybase",
        user="flybase",
        password="flybase",
        connect_timeout=30,
    )


def find_publications(cur, fbco_id):
    """Get all publications linked to a combination via feature_pub."""
    cur.execute(
        """
        SELECT
            p.uniquename AS fbrf,
            p.title,
            p.pyear AS year,
            p.miniref,
            ct.name AS pub_type
        FROM feature f
        JOIN feature_pub fp ON f.feature_id = fp.feature_id
        JOIN pub p ON fp.pub_id = p.pub_id
        JOIN cvterm ct ON p.type_id = ct.cvterm_id
        WHERE f.uniquename = %(uid)s
          AND f.is_obsolete = false
        ORDER BY p.pyear DESC, p.uniquename
        """,
        {"uid": fbco_id},
    )
    pub_rows = cur.fetchall()
    if not pub_rows:
        print(f"No publications found for {fbco_id}")
        return

    df = pd.DataFrame(
        pub_rows, columns=["fbrf", "title", "year", "miniref", "pub_type"]
    )

    # Get external IDs (DOI, PMID, PMCID) for all these pubs
    fbrfs = [r[0] for r in pub_rows]
    cur.execute(
        """
        SELECT p.uniquename AS fbrf, db.name AS db_name, dx.accession
        FROM pub p
        JOIN pub_dbxref pdx ON p.pub_id = pdx.pub_id
        JOIN dbxref dx ON pdx.dbxref_id = dx.dbxref_id
        JOIN db ON dx.db_id = db.db_id
        WHERE p.uniquename = ANY(%(fbrfs)s)
          AND db.name IN ('DOI', 'pubmed', 'PMCID')
        """,
        {"fbrfs": fbrfs},
    )
    xref_rows = cur.fetchall()

    # Pivot external IDs into columns
    doi_map = {}
    pmid_map = {}
    pmcid_map = {}
    for fbrf, db_name, accession in xref_rows:
        if db_name == "DOI":
            doi_map[fbrf] = accession
        elif db_name == "pubmed":
            pmid_map[fbrf] = accession
        elif db_name == "PMCID":
            pmcid_map[fbrf] = accession

    df["doi"] = df["fbrf"].map(doi_map).fillna("")
    df["pmid"] = df["fbrf"].map(pmid_map).fillna("")
    df["pmcid"] = df["fbrf"].map(pmcid_map).fillna("")

    print(f"Found {len(df)} publication(s) for {fbco_id}")
    print(df.to_csv(sep="\t", index=False))


def main():
    if len(sys.argv) != 2:
        print("Usage: find_combo_pubs.py <FBco_ID>")
        sys.exit(1)

    fbco_id = sys.argv[1].strip()
    if not fbco_id.startswith("FBco"):
        print(f"Error: expected FBco ID, got '{fbco_id}'")
        sys.exit(1)

    conn = connect()
    cur = conn.cursor()
    find_publications(cur, fbco_id)
    conn.close()


if __name__ == "__main__":
    main()
