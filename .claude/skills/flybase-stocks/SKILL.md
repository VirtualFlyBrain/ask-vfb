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

All Python commands use the `.venv` created by `setup_venv.sh`.

**Before running any query**, verify the venv exists:
```bash
ls .venv/bin/python
```
If it does not exist, run `bash setup_venv.sh` and wait for it to complete before proceeding.

Query scripts live in `.claude/skills/flybase-stocks/scripts/` and are run via:

```bash
.venv/bin/python .claude/skills/flybase-stocks/scripts/<script>.py <args>
```

**Never use the system Python.**

### Database connection

All queries connect to the FlyBase public Chado database using `psycopg`:

- **Host:** `chado.flybase.org`
- **User:** `flybase`
- **Password:** `flybase`
- **Database:** `flybase`

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

Run:

```bash
.venv/bin/python .claude/skills/flybase-stocks/scripts/resolve_entity.py "<entity>"
```

The script tries three progressively broader searches:
1. **Exact match** on `feature.name`
2. **Synonym match** via the `synonym` table (case-insensitive)
3. **Broad match** with `ILIKE '%<name>%'`

For FlyBase IDs (FBgn/FBal/FBti/FBst), it verifies the ID exists directly.

Output is prefixed with the match type: `EXACT MATCH`, `SYNONYM MATCH`, `BROAD MATCH`, or `NOT FOUND`.

**Important: when a match is found via synonym** (i.e. the user's input does not match `f.name` exactly), always confirm with the user before proceeding. Show them the resolved current symbol and ask them to confirm. For example:

> Your search for "CG11340" matched **pHCl-2** (FBgn0039840, gene) via synonym. Shall I find stocks for this gene?

Only proceed to Step 3 after the user confirms. **STOP and wait for the user's reply — do not answer your own question or assume confirmation.**

**If multiple matches are found** (whether by exact name or synonym), show a disambiguation list with name, ID, type (and matched synonym if applicable), and ask the user to confirm which one. **STOP and wait for the user's reply.**

**If no match is found** by any method, report to the user and suggest checking spelling or using a FlyBase ID.

---

### Step 3: Find stocks

Run:

```bash
.venv/bin/python .claude/skills/flybase-stocks/scripts/find_stocks.py <FBxx_ID> [collection_filter]
```

The script automatically selects the correct query based on the ID prefix:

- **FBgn** (gene) — finds stocks via four UNION paths:
  1. **Direct allele path**: gene → allele (alleleof) → feature_genotype → genotype → stock
  2. **Allele→construct→insertion path**: gene → allele → FBtp → FBti (producedby) → genotype → stock
  3. **Allele→insertion path**: gene → allele → insertion (associated_with) → genotype → stock
  4. **Regulatory region path**: gene → regulatory_region → allele → FBtp → FBti → genotype → stock

- **FBal** (allele) — finds stocks via three UNION paths:
  1. **Direct**: allele → feature_genotype → genotype → stock
  2. **Via construct→insertion**: allele → FBtp → FBti (producedby) → genotype → stock
  3. **Via associated insertion**: allele → insertion (associated_with) → genotype → stock

- **FBti** (insertion/aberration) — finds stocks directly via feature_genotype → genotype → stock

- **FBst** (stock ID) — looks up stock details directly

The optional `collection_filter` argument filters by stock collection name (e.g. "Bloomington", "Kyoto", "VDRC").

Timeouts are set automatically: 120s for gene queries, 60s for allele/insertion queries.

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
| `.venv` not found | Run `bash setup_venv.sh` automatically |
| `psycopg` import error | Run `bash setup_venv.sh` to install dependencies |
| Connection timeout | Retry once; if it fails again, report that `chado.flybase.org` may be temporarily unavailable |
| Feature not found | Try broader ILIKE search; suggest checking spelling or using a FlyBase ID |
| No stocks found | Report that no stocks are currently available for this entity in FlyBase; suggest checking FlyBase directly |
| Ambiguous name (multiple matches) | Show disambiguation list with IDs and types; ask user to pick |

---

## Testing

Integration tests live in `tests/` and run against the live FlyBase Chado database using pytest:

```bash
.venv/bin/python -m pytest .claude/skills/flybase-stocks/tests/ -v --rootdir=.claude/skills/flybase-stocks
```

**After any change to the scripts or queries in this skill**, ask the user whether they'd like you to run the test suite before considering the change complete.

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
- The gene UNION query joins four paths and can be slow for broadly-used genes; `statement_timeout=120000` (120s) for gene queries
- For allele/insertion queries (single path), `statement_timeout=60000` (60s) is sufficient
- All queries use parameterised queries to prevent SQL injection
- Scripts use `psycopg` cursors directly (not `pd.read_sql_query`) to avoid SQLAlchemy compatibility warnings
