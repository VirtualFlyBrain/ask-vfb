---
name: flybase-combo-pubs
description: Find publications linked to FlyBase split system combinations (FBco) by querying FlyBase public Chado database
user-invocable: true
argument-hint: "<combination name, synonym, or FBco ID>"
---

# FlyBase Combination Publications Finder

Find publications linked to Drosophila split system combinations (FBco) by querying the FlyBase public Chado (PostgreSQL) database. Supports lookup by FBco ID, full combination name, or common synonym (e.g. "MB002B").

---

## Setup

All Python commands use the `.venv` created by `setup_venv.sh`.

**Before running any query**, verify the venv exists:
```bash
ls .venv/bin/python
```
If it does not exist, run `bash setup_venv.sh` and wait for it to complete before proceeding.

Query scripts live in `.claude/skills/flybase-combo-pubs/scripts/` and are run via:

```bash
.venv/bin/python .claude/skills/flybase-combo-pubs/scripts/<script>.py <args>
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

- **Entity**: a combination synonym (e.g. `MB002B`), full combination name, or FlyBase ID (e.g. `FBco0000052`)
- **Search mode**: infer from the entity format:

| Input pattern | Mode |
|---|---|
| `FBco\d+` | Combination ID — resolve directly |
| Any other string | Name or synonym — search by name then synonym |

---

### Step 2: Resolve the combination

Run:

```bash
.venv/bin/python .claude/skills/flybase-combo-pubs/scripts/resolve_combination.py "<entity>"
```

The script tries three progressively broader searches:
1. **Exact match** on `feature.name`
2. **Synonym match** via the `synonym` table
3. **Broad match** with `ILIKE '%<name>%'`

For FBco IDs, it verifies the ID exists directly.

Output is prefixed with the match type: `EXACT MATCH`, `SYNONYM MATCH`, `BROAD MATCH`, or `NOT FOUND`.

**Important: when a match is found via synonym** (i.e. the user's input does not match `f.name` exactly), always confirm with the user before proceeding. Show them the resolved combination symbol and ask them to confirm. For example:

> Your search for "MB002B" matched **Scer\GAL4[DBD.R14C08]∩Hsap\RELA[AD.R12C11]** (FBco0000052) via synonym. Shall I find publications for this combination?

Only proceed to Step 3 after the user confirms. **STOP and wait for the user's reply — do not answer your own question or assume confirmation.**

**If multiple matches are found**, show a disambiguation list with name and ID, and ask the user to confirm which one. **STOP and wait for the user's reply.**

**If no match is found** by any method, report to the user and suggest checking spelling or using a FlyBase ID.

---

### Step 3: Find publications

Run:

```bash
.venv/bin/python .claude/skills/flybase-combo-pubs/scripts/find_combo_pubs.py <FBco_ID>
```

The script returns publications linked via the `feature_pub` table with:
- FBrf ID, title, year, miniref (short citation), publication type
- External identifiers: DOI, PMID, PMCID (where available)

Results are sorted by year descending.

---

### Step 4: Present results

Always include a **query summary**:

```
Query:
- Combination: Scer\GAL4[DBD.R14C08]∩Hsap\RELA[AD.R12C11] (FBco0000052)
- Synonym used: MB002B

Results: 6 publications (2014–2022)
```

For each publication, show:
- **Title** with year
- **Citation** (miniref)
- **Links**: FlyBase (`https://flybase.org/reports/{FBrf_ID}`), DOI (`https://doi.org/{DOI}`), PubMed (`https://pubmed.ncbi.nlm.nih.gov/{PMID}/`) — only include links where the identifier exists

**Also include a FlyBase report link** for the combination: `https://flybase.org/reports/{FBco_ID}`

---

### Step 5: Closing offer

After presenting results, offer relevant follow-ups:

- **Full text**: "I can fetch the full text of any of these papers via Europe PMC."
- **More detail**: "I can look up detailed metadata (authors, abstract) for any of these publications."
- **Related searches**: "I can search for other combinations that share a component allele, or look up stocks for this combination."

---

## Error paths

| Situation | Behaviour |
|---|---|
| `.venv` not found | Run `bash setup_venv.sh` automatically |
| `psycopg` import error | Run `bash setup_venv.sh` to install dependencies |
| Connection timeout | Retry once; if it fails again, report that `chado.flybase.org` may be temporarily unavailable |
| Combination not found | Try broader ILIKE search; suggest checking spelling or using a FlyBase ID |
| No publications found | Report that no publications are currently linked for this combination in FlyBase |
| Ambiguous name (multiple matches) | Show disambiguation list with IDs; ask user to pick |

---

## Testing

Integration tests live in `tests/` and run against the live FlyBase Chado database using pytest:

```bash
.venv/bin/python -m pytest .claude/skills/flybase-combo-pubs/tests/ -v --rootdir=.claude/skills/flybase-combo-pubs
```

**After any change to the scripts or queries in this skill**, ask the user whether they'd like you to run the test suite before considering the change complete.

---

## Notes

- Combinations in FlyBase have feature type `split system combination`
- The `feature_pub` table links combinations to publications directly
- Publication external IDs (DOI, PMID, PMCID) are in `pub_dbxref` joined via `dbxref` and `db`
- Combinations often have common synonyms (e.g. MB002B for FBco0000052) stored in `feature_synonym`
- The `pub.miniref` field contains a compact citation string (e.g. "Aso et al., 2014, eLife 3: e04577")
- All queries use parameterised queries to prevent SQL injection
- Scripts use `psycopg` cursors directly (not `pd.read_sql_query`)
