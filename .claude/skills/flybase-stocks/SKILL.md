---
name: flybase-stocks
description: Find fly stocks for genes, alleles, or insertions by querying FlyBase public Chado database
user-invocable: true
argument-hint: "<gene, allele, or insertion name or FBgn/FBal/FBti ID>"
---

# FlyBase Stock Finder

Find available Drosophila fly stocks carrying a given gene, allele, or insertion by querying the FlyBase public Chado (PostgreSQL) database.

---

## Setup

All queries use `psql` against the FlyBase public Chado database:

- **Host:** `chado.flybase.org`
- **User:** `flybase`
- **Password:** `flybase`
- **Database:** `flybase`

Prefix every query with:

```bash
PGPASSWORD=flybase psql -h chado.flybase.org -U flybase -d flybase -c "..."
```

---

## Instructions

### Step 1: Parse input

Extract from the user's request:

- **Entity**: a gene name (e.g. `dpp`), allele symbol (e.g. `dpp[H46]`), insertion symbol (e.g. `P{GAL4-da.G32}UH1`), or FlyBase ID (e.g. `FBgn0000490`, `FBal0003059`, `FBti0002191`)
- **Collection filter** (optional): a specific stock centre to filter by (e.g. "Bloomington", "Kyoto", "VDRC")
- **Search mode**: infer from the entity format:

| Input pattern | Mode |
|---|---|
| `FBgn\d+` | Gene ID — find stocks via alleles of this gene |
| `FBal\d+` | Allele ID — find stocks directly |
| `FBti\d+` | Insertion ID — find stocks directly |
| `FBst\d+` | Stock ID — look up stock details directly |
| Name containing `[` or `{` | Likely allele or insertion symbol — search by name |
| Plain name (e.g. `dpp`, `white`) | Gene symbol — find gene then stocks via alleles |

---

### Step 2: Resolve the entity

**If a FlyBase ID is provided**, verify it exists:

```sql
SELECT f.name, f.uniquename, c.name AS type
FROM feature f
JOIN cvterm c ON f.type_id = c.cvterm_id
WHERE f.uniquename = '<ID>' AND f.is_obsolete = false;
```

**If a name/symbol is provided**, first try an exact match on `feature.name`:

```sql
SELECT DISTINCT f.name, f.uniquename, c.name AS type
FROM feature f
JOIN cvterm c ON f.type_id = c.cvterm_id
WHERE f.is_obsolete = false
  AND c.name IN ('gene', 'allele', 'transposable_element_insertion_site', 'chromosome_structure_variation')
  AND f.name = '<name>'
ORDER BY c.name, f.name
LIMIT 20;
```

**If no exact match is found**, fall back to a synonym search:

```sql
SELECT DISTINCT f.name, f.uniquename, c.name AS type, syn.name AS matched_synonym
FROM feature f
JOIN cvterm c ON f.type_id = c.cvterm_id
JOIN feature_synonym fs ON f.feature_id = fs.feature_id
JOIN synonym syn ON fs.synonym_id = syn.synonym_id
WHERE f.is_obsolete = false
  AND c.name IN ('gene', 'allele', 'transposable_element_insertion_site', 'chromosome_structure_variation')
  AND syn.name ILIKE '<name>'
ORDER BY c.name, f.name
LIMIT 20;
```

**Important: when a match is found via synonym** (i.e. the user's input does not match `f.name` exactly), always confirm with the user before proceeding. Show them the resolved current symbol and ask them to confirm. For example:

> Your search for "CG11340" matched **pHCl-2** (FBgn0039840, gene) via synonym. Shall I find stocks for this gene?

Only proceed to Step 3 after the user confirms. **STOP and wait for the user's reply — do not answer your own question or assume confirmation.**

**If multiple matches are found** (whether by exact name or synonym), show a disambiguation list with name, ID, type (and matched synonym if applicable), and ask the user to confirm which one. **STOP and wait for the user's reply.**

**If no match is found** by either exact name or synonym, try a broader search with `ILIKE '%<name>%'` on both `f.name` and `syn.name`. Show results and ask the user to pick one. **STOP and wait for the user's reply.**

---

### Step 3: Find stocks

The query depends on the feature type identified in Step 2.

**For a gene (FBgn)** — find all associated stocks via four paths:

Stocks in FlyBase connect to genes through multiple routes. The following UNION query covers all four paths and matches the results shown on the FlyBase website hitlist (`/hitlist/<FBgn>/to/FBst`):

1. **Direct allele path**: gene → allele (alleleof) → feature_genotype → genotype → stock
2. **Allele→construct→insertion path**: gene → allele → transgenic_transposable_element (FBtp) → insertion (FBti, via producedby) → feature_genotype → genotype → stock
3. **Allele→insertion path**: gene → allele → insertion (via associated_with; includes `transposable_element_insertion_site`, `insertion_site`, and `insertion` types) → feature_genotype → genotype → stock
4. **Regulatory region path**: gene → regulatory_region (associated_with) → allele (has_reg_region) → FBtp → FBti → feature_genotype → genotype → stock

```sql
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
  WHERE gene.uniquename = '<FBgn_ID>'

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
  WHERE gene.uniquename = '<FBgn_ID>'

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
  WHERE gene.uniquename = '<FBgn_ID>'

  UNION

  -- Path 4: gene -> regulatory_region -> allele (of other gene) -> FBtp -> FBti -> genotype -> stock
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
  WHERE gene.uniquename = '<FBgn_ID>'
)
SELECT stock_id, stock_number, genotype, collection
FROM all_stocks
ORDER BY collection, stock_number;
```

**For an allele (FBal)** — find stocks via three paths:

Some alleles have no direct `feature_genotype` entries but connect to stocks through associated insertions or constructs. Use a UNION to cover all paths:

1. **Direct**: allele → feature_genotype → genotype → stock
2. **Via construct→insertion**: allele → FBtp (transgenic_transposable_element) → FBti (insertion, producedby) → feature_genotype → genotype → stock
3. **Via associated insertion**: allele → insertion (associated_with) → feature_genotype → genotype → stock

```sql
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
  WHERE f.uniquename = '<FBal_ID>' AND f.is_obsolete = false

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
  WHERE f.uniquename = '<FBal_ID>' AND f.is_obsolete = false

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
  WHERE f.uniquename = '<FBal_ID>' AND f.is_obsolete = false
)
SELECT stock_id, stock_number, genotype, collection
FROM all_stocks
ORDER BY collection, stock_number;
```

**For an insertion (FBti) or chromosome aberration** — find stocks directly:

```sql
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
WHERE f.uniquename = '<feature_ID>'
  AND f.is_obsolete = false
  AND s.is_obsolete = false
ORDER BY sc.uniquename, s.name;
```

**If the user specified a stock collection filter**, append to the WHERE clause:

```sql
AND sc.uniquename ILIKE '%<collection_filter>%'
```

**For a stock ID (FBst)** — look up stock details directly:

```sql
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
WHERE s.uniquename = '<FBst_ID>'
  AND s.is_obsolete = false;
```

---

### Step 4: Present results

Always include a **query summary**:

```
Query:
- Entity:      dpp (FBgn0000490, gene)
- Search mode: gene → alleles → stocks
- Collection:  (all)

Results: 45 stocks across 12 alleles from 3 stock centres
```

**If results are small (≤30 rows)**, show the full table.

**If results are large (>30 rows)**, show:
1. Total stock count and allele count
2. Breakdown by stock collection
3. Top 20 rows (sorted by collection, then allele name)
4. Note that results are truncated

**Stock centre links** — for each stock, provide the catalogue URL:

| Collection | URL pattern |
|---|---|
| Bloomington Drosophila Stock Center | `https://bdsc.indiana.edu/stock/{stock_number}` |
| Kyoto Stock Center | `https://kyotofly.kit.jp/cgi-bin/stocks/search_res_det.cgi?DB_NUM=1&DG_NUM={stock_number}` |
| Vienna Drosophila Resource Center | `https://stockcenter.vdrc.at/control/product/~VIEW_INDEX~0/~VIEW_SIZE~100/~product_id~{stock_number}` |

Where `{stock_number}` is the value from the `stock_number` / `s.name` column.

For other collections, provide the FlyBase stock report link: `https://flybase.org/reports/{stock_id}`

**Always include a FlyBase report link** for the queried entity:
- Gene: `https://flybase.org/reports/{FBgn_ID}`
- Allele: `https://flybase.org/reports/{FBal_ID}`
- Stock: `https://flybase.org/reports/{FBst_ID}`

---

### Step 5: Closing offer

After presenting results, offer relevant follow-ups:

- **Filter by collection**: "I can filter these to show only stocks from a specific centre (Bloomington, Kyoto, VDRC, etc.)."
- **Specific allele**: "To see stocks for a specific allele, just give me the allele symbol or ID."
- **Genotype details**: "I can look up the full genotype for any stock listed."
- **Save results**: If requested, save to `outputs/stocks_{entity}_{timestamp}.csv`.

---

## Error paths

| Situation | Behaviour |
|---|---|
| `psql` not installed | Tell user to install PostgreSQL client: `brew install libpq` |
| Connection timeout | Retry once; if it fails again, report that `chado.flybase.org` may be temporarily unavailable |
| Feature not found | Try broader ILIKE search; suggest checking spelling or using a FlyBase ID |
| No stocks found | Report that no stocks are currently available for this entity in FlyBase; suggest checking FlyBase directly |
| Ambiguous name (multiple matches) | Show disambiguation list with IDs and types; ask user to pick |

---

## Notes

- The seven stock collections in FlyBase are: Bloomington Drosophila Stock Center, Kyoto Stock Center, Vienna Drosophila Resource Center, National Drosophila Species Stock Center, FlyORF, Korea Drosophila Resource Center, National Institute of Genetics Fly Stocks
- Gene-to-stock paths (four routes, combined via UNION):
  1. Direct: `gene → allele (alleleof) → feature_genotype → genotype → stock`
  2. Via construct: `gene → allele → FBtp (transgenic_transposable_element) → FBti (insertion, producedby) → feature_genotype → genotype → stock`
  3. Via associated insertion: `gene → allele → insertion (associated_with, types: transposable_element_insertion_site, insertion_site, insertion) → feature_genotype → genotype → stock`
  4. Via regulatory region: `gene → regulatory_region (associated_with) → allele (has_reg_region) → FBtp → FBti → feature_genotype → genotype → stock`
- All four paths are needed to match the FlyBase website hitlist results (`/hitlist/<FBgn>/to/FBst`)
- Allele-to-stock paths (three routes, combined via UNION):
  1. Direct: `allele → feature_genotype → genotype → stock`
  2. Via construct: `allele → FBtp → FBti (producedby) → feature_genotype → genotype → stock`
  3. Via associated insertion: `allele → insertion (associated_with) → feature_genotype → genotype → stock`
- Insertion/aberration-to-stock path: `feature → feature_genotype → genotype → stock_genotype → stock`
- Stock collections are linked via `stockcollection_stock` (not `stock_stockcollection`)
- The `stock.name` field contains the stock centre catalogue number (e.g. "7144" for BDSC #7144)
- The `genotype.uniquename` field contains the human-readable genotype string (e.g. `Df(2L)BSC37, dpp[EP2232]/CyO`)
- The gene UNION query joins four paths and can be slow for broadly-used genes; set a 120-second timeout on psql commands for gene queries
- For allele/insertion queries (single path), a 60-second timeout is sufficient
