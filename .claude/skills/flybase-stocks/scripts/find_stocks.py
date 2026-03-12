"""Find FlyBase stocks for a given feature ID (FBgn, FBal, FBti, or FBst)."""
import sys
import psycopg
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


def find_stocks_gene(conn, gene_id, collection_filter=None):
    """Find stocks for a gene via four UNION paths."""
    query = """
WITH all_stocks AS (
  -- Path 1: gene -> allele -> genotype -> stock (direct)
  SELECT DISTINCT s.uniquename AS stock_id, s.name AS stock_number,
         g.uniquename AS genotype, sc.uniquename AS collection
  FROM feature gene
  JOIN feature_relationship fr ON gene.feature_id = fr.object_id
  JOIN cvterm frt ON fr.type_id = frt.cvterm_id AND frt.name = 'alleleof'
  JOIN feature a ON fr.subject_id = a.feature_id AND a.is_obsolete = false
  JOIN feature_genotype fg ON a.feature_id = fg.feature_id
  JOIN genotype g ON fg.genotype_id = g.genotype_id
  JOIN stock_genotype sg ON g.genotype_id = sg.genotype_id
  JOIN stock s ON sg.stock_id = s.stock_id AND s.is_obsolete = false
  LEFT JOIN stockcollection_stock scs ON s.stock_id = scs.stock_id
  LEFT JOIN stockcollection sc ON scs.stockcollection_id = sc.stockcollection_id
  WHERE gene.uniquename = %(feature_id)s

  UNION

  -- Path 2: gene -> allele -> FBtp (construct) -> FBti (insertion) -> genotype -> stock
  SELECT DISTINCT s.uniquename, s.name, g.uniquename, sc.uniquename
  FROM feature gene
  JOIN feature_relationship fr1 ON gene.feature_id = fr1.object_id
  JOIN cvterm c1 ON fr1.type_id = c1.cvterm_id AND c1.name = 'alleleof'
  JOIN feature a ON fr1.subject_id = a.feature_id AND a.is_obsolete = false
  JOIN feature_relationship fr2 ON a.feature_id = fr2.subject_id
  JOIN feature tp ON fr2.object_id = tp.feature_id
  JOIN cvterm ctp ON tp.type_id = ctp.cvterm_id
    AND ctp.name = 'transgenic_transposable_element'
  JOIN feature_relationship fr3 ON tp.feature_id = fr3.object_id
  JOIN cvterm c3 ON fr3.type_id = c3.cvterm_id AND c3.name = 'producedby'
  JOIN feature ti ON fr3.subject_id = ti.feature_id AND ti.is_obsolete = false
  JOIN feature_genotype fg ON ti.feature_id = fg.feature_id
  JOIN genotype g ON fg.genotype_id = g.genotype_id
  JOIN stock_genotype sg ON g.genotype_id = sg.genotype_id
  JOIN stock s ON sg.stock_id = s.stock_id AND s.is_obsolete = false
  LEFT JOIN stockcollection_stock scs ON s.stock_id = scs.stock_id
  LEFT JOIN stockcollection sc ON scs.stockcollection_id = sc.stockcollection_id
  WHERE gene.uniquename = %(feature_id)s

  UNION

  -- Path 3: gene -> allele -> associated_with FBti (insertion) -> genotype -> stock
  SELECT DISTINCT s.uniquename, s.name, g.uniquename, sc.uniquename
  FROM feature gene
  JOIN feature_relationship fr1 ON gene.feature_id = fr1.object_id
  JOIN cvterm c1 ON fr1.type_id = c1.cvterm_id AND c1.name = 'alleleof'
  JOIN feature a ON fr1.subject_id = a.feature_id AND a.is_obsolete = false
  JOIN feature_relationship fr2 ON a.feature_id = fr2.subject_id
  JOIN cvterm c2 ON fr2.type_id = c2.cvterm_id AND c2.name = 'associated_with'
  JOIN feature ti ON fr2.object_id = ti.feature_id AND ti.is_obsolete = false
  JOIN cvterm cti ON ti.type_id = cti.cvterm_id
    AND cti.name IN ('transposable_element_insertion_site', 'insertion_site', 'insertion')
  JOIN feature_genotype fg ON ti.feature_id = fg.feature_id
  JOIN genotype g ON fg.genotype_id = g.genotype_id
  JOIN stock_genotype sg ON g.genotype_id = sg.genotype_id
  JOIN stock s ON sg.stock_id = s.stock_id AND s.is_obsolete = false
  LEFT JOIN stockcollection_stock scs ON s.stock_id = scs.stock_id
  LEFT JOIN stockcollection sc ON scs.stockcollection_id = sc.stockcollection_id
  WHERE gene.uniquename = %(feature_id)s

  UNION

  -- Path 4: gene -> regulatory_region -> allele -> FBtp -> FBti -> genotype -> stock
  SELECT DISTINCT s.uniquename, s.name, g.uniquename, sc.uniquename
  FROM feature gene
  JOIN feature_relationship fr1 ON gene.feature_id = fr1.object_id
  JOIN cvterm c1 ON fr1.type_id = c1.cvterm_id AND c1.name = 'associated_with'
  JOIN feature rr ON fr1.subject_id = rr.feature_id
  JOIN cvterm ctr ON rr.type_id = ctr.cvterm_id AND ctr.name = 'regulatory_region'
  JOIN feature_relationship fr2 ON rr.feature_id = fr2.object_id
  JOIN cvterm c2 ON fr2.type_id = c2.cvterm_id AND c2.name = 'has_reg_region'
  JOIN feature a ON fr2.subject_id = a.feature_id AND a.is_obsolete = false
  JOIN feature_relationship fr3 ON a.feature_id = fr3.subject_id
  JOIN feature tp ON fr3.object_id = tp.feature_id
  JOIN cvterm ctp ON tp.type_id = ctp.cvterm_id
    AND ctp.name = 'transgenic_transposable_element'
  JOIN feature_relationship fr4 ON tp.feature_id = fr4.object_id
  JOIN cvterm c4 ON fr4.type_id = c4.cvterm_id AND c4.name = 'producedby'
  JOIN feature ti ON fr4.subject_id = ti.feature_id AND ti.is_obsolete = false
  JOIN feature_genotype fg ON ti.feature_id = fg.feature_id
  JOIN genotype g ON fg.genotype_id = g.genotype_id
  JOIN stock_genotype sg ON g.genotype_id = sg.genotype_id
  JOIN stock s ON sg.stock_id = s.stock_id AND s.is_obsolete = false
  LEFT JOIN stockcollection_stock scs ON s.stock_id = scs.stock_id
  LEFT JOIN stockcollection sc ON scs.stockcollection_id = sc.stockcollection_id
  WHERE gene.uniquename = %(feature_id)s
)
SELECT stock_id, stock_number, genotype, collection
FROM all_stocks
"""
    params = {"feature_id": gene_id}
    if collection_filter:
        query += "WHERE collection ILIKE %(coll)s\n"
        params["coll"] = collection_filter
    query += "ORDER BY collection, stock_number;"
    return run_query(conn, query, params)


def find_stocks_allele(conn, allele_id, collection_filter=None):
    """Find stocks for an allele via three UNION paths."""
    query = """
WITH all_stocks AS (
  -- Path 1: allele -> genotype -> stock (direct)
  SELECT DISTINCT s.uniquename AS stock_id, s.name AS stock_number,
         g.uniquename AS genotype, sc.uniquename AS collection
  FROM feature f
  JOIN feature_genotype fg ON f.feature_id = fg.feature_id
  JOIN genotype g ON fg.genotype_id = g.genotype_id
  JOIN stock_genotype sg ON g.genotype_id = sg.genotype_id
  JOIN stock s ON sg.stock_id = s.stock_id AND s.is_obsolete = false
  LEFT JOIN stockcollection_stock scs ON s.stock_id = scs.stock_id
  LEFT JOIN stockcollection sc ON scs.stockcollection_id = sc.stockcollection_id
  WHERE f.uniquename = %(feature_id)s AND f.is_obsolete = false

  UNION

  -- Path 2: allele -> FBtp (construct) -> FBti (insertion) -> genotype -> stock
  SELECT DISTINCT s.uniquename, s.name, g.uniquename, sc.uniquename
  FROM feature f
  JOIN feature_relationship fr1 ON f.feature_id = fr1.subject_id
  JOIN feature tp ON fr1.object_id = tp.feature_id
  JOIN cvterm ctp ON tp.type_id = ctp.cvterm_id
    AND ctp.name = 'transgenic_transposable_element'
  JOIN feature_relationship fr2 ON tp.feature_id = fr2.object_id
  JOIN cvterm c2 ON fr2.type_id = c2.cvterm_id AND c2.name = 'producedby'
  JOIN feature ti ON fr2.subject_id = ti.feature_id AND ti.is_obsolete = false
  JOIN feature_genotype fg ON ti.feature_id = fg.feature_id
  JOIN genotype g ON fg.genotype_id = g.genotype_id
  JOIN stock_genotype sg ON g.genotype_id = sg.genotype_id
  JOIN stock s ON sg.stock_id = s.stock_id AND s.is_obsolete = false
  LEFT JOIN stockcollection_stock scs ON s.stock_id = scs.stock_id
  LEFT JOIN stockcollection sc ON scs.stockcollection_id = sc.stockcollection_id
  WHERE f.uniquename = %(feature_id)s AND f.is_obsolete = false

  UNION

  -- Path 3: allele -> associated_with insertion -> genotype -> stock
  SELECT DISTINCT s.uniquename, s.name, g.uniquename, sc.uniquename
  FROM feature f
  JOIN feature_relationship fr1 ON f.feature_id = fr1.subject_id
  JOIN cvterm c1 ON fr1.type_id = c1.cvterm_id AND c1.name = 'associated_with'
  JOIN feature ti ON fr1.object_id = ti.feature_id AND ti.is_obsolete = false
  JOIN cvterm cti ON ti.type_id = cti.cvterm_id
    AND cti.name IN ('transposable_element_insertion_site', 'insertion_site', 'insertion')
  JOIN feature_genotype fg ON ti.feature_id = fg.feature_id
  JOIN genotype g ON fg.genotype_id = g.genotype_id
  JOIN stock_genotype sg ON g.genotype_id = sg.genotype_id
  JOIN stock s ON sg.stock_id = s.stock_id AND s.is_obsolete = false
  LEFT JOIN stockcollection_stock scs ON s.stock_id = scs.stock_id
  LEFT JOIN stockcollection sc ON scs.stockcollection_id = sc.stockcollection_id
  WHERE f.uniquename = %(feature_id)s AND f.is_obsolete = false
)
SELECT stock_id, stock_number, genotype, collection
FROM all_stocks
"""
    params = {"feature_id": allele_id}
    if collection_filter:
        query += "WHERE collection ILIKE %(coll)s\n"
        params["coll"] = collection_filter
    query += "ORDER BY collection, stock_number;"
    return run_query(conn, query, params)


def find_stocks_insertion(conn, feature_id, collection_filter=None):
    """Find stocks for an insertion or chromosome aberration."""
    query = """
SELECT DISTINCT
    f.name AS feature_name,
    f.uniquename AS feature_id,
    s.name AS stock_number,
    s.uniquename AS stock_id,
    g.uniquename AS genotype,
    sc.uniquename AS collection
FROM feature f
JOIN feature_genotype fg ON f.feature_id = fg.feature_id
JOIN genotype g ON fg.genotype_id = g.genotype_id
JOIN stock_genotype sg ON g.genotype_id = sg.genotype_id
JOIN stock s ON sg.stock_id = s.stock_id
LEFT JOIN stockcollection_stock scs ON s.stock_id = scs.stock_id
LEFT JOIN stockcollection sc ON scs.stockcollection_id = sc.stockcollection_id
WHERE f.uniquename = %(feature_id)s
  AND f.is_obsolete = false
  AND s.is_obsolete = false
"""
    params = {"feature_id": feature_id}
    if collection_filter:
        query += "  AND sc.uniquename ILIKE %(coll)s\n"
        params["coll"] = collection_filter
    query += "ORDER BY sc.uniquename, s.name;"
    return run_query(conn, query, params)


def find_stock_details(conn, stock_id):
    """Look up details for a specific stock ID."""
    return run_query(conn, """
        SELECT
            s.name AS stock_number,
            s.uniquename AS stock_id,
            s.description,
            sc.uniquename AS collection,
            g.uniquename AS genotype
        FROM stock s
        LEFT JOIN stockcollection_stock scs ON s.stock_id = scs.stock_id
        LEFT JOIN stockcollection sc ON scs.stockcollection_id = sc.stockcollection_id
        LEFT JOIN stock_genotype sg ON s.stock_id = sg.stock_id
        LEFT JOIN genotype g ON sg.genotype_id = g.genotype_id
        WHERE s.uniquename = %(stock_id)s
          AND s.is_obsolete = false
    """, {"stock_id": stock_id})


def main():
    if len(sys.argv) < 2:
        print("Usage: find_stocks.py <FBgn/FBal/FBti/FBst_ID> [collection_filter]")
        sys.exit(1)

    feature_id = sys.argv[1]
    collection_filter = sys.argv[2] if len(sys.argv) > 2 else None
    if collection_filter:
        collection_filter = "%" + collection_filter + "%"

    # Determine timeout based on query type
    timeout = 120000 if feature_id.startswith("FBgn") else 60000

    conn = psycopg.connect(
        host="chado.flybase.org",
        dbname="flybase",
        user="flybase",
        password="flybase",
        connect_timeout=10,
        options="-c statement_timeout=" + str(timeout),
    )

    try:
        if feature_id.startswith("FBgn"):
            df = find_stocks_gene(conn, feature_id, collection_filter)
        elif feature_id.startswith("FBal"):
            df = find_stocks_allele(conn, feature_id, collection_filter)
        elif feature_id.startswith("FBti"):
            df = find_stocks_insertion(conn, feature_id, collection_filter)
        elif feature_id.startswith("FBst"):
            df = find_stock_details(conn, feature_id)
        else:
            print("ERROR: Unrecognised ID prefix. Expected FBgn, FBal, FBti, or FBst.")
            sys.exit(1)

        print(str(len(df)) + " stocks found")
        if len(df) > 0:
            print(df.to_string(index=False))
    finally:
        conn.close()


if __name__ == "__main__":
    main()
