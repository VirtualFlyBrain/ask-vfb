---
name: vfb-connectivity
description: Query synaptic connectivity between Drosophila neuron classes using VFB — supports upstream/downstream filtering, weight thresholds, and class-level aggregation. DO NOT USE FOR FINDING CONNECTIONS ON INDIVIDUAL NEURONS OR FOR CONNECTIONS BETWEEN MUSCLES & NEURONS OR SENSE ORGANS AND NEURONS.
user-invocable: true
---

# VFB Neuron Connectivity Query

Query synaptic connections between Drosophila neuron types using `vfb_connect.get_connected_neurons_by_type`. Returns per-neuron or class-aggregated connectivity data from the VirtualFlyBrain knowledge graph.

---

## Setup

All Python commands use the `.venv` created by `setup_venv.sh`. If `.venv` is missing, run `bash setup_venv.sh` automatically before proceeding.

Query scripts live in `.claude/skills/vfb-connectivity/scripts/` and are run via:

```bash
.venv/bin/python .claude/skills/vfb-connectivity/scripts/<script>.py <args>
```

**Never use the system Python.** If `.venv` is missing, run `bash setup_venv.sh` automatically before proceeding with any queries.

### Session initialisation

When this skill is first invoked in a new session, fetch the available connectome datasets and cache the result for use throughout the session:

```bash
.venv/bin/python .claude/skills/vfb-connectivity/scripts/list_datasets.py
```

This prints each dataset's label and symbol. Use the symbols when constructing `--exclude-dbs` arguments. Present the dataset list to the user when confirming query parameters (Step 1).

---

## Instructions

### Step 1: Parse input

Extract from the user's request:

- **Upstream neuron type**: e.g. `"GABAergic neuron"`, `"Kenyon cell"`, `"olfactory receptor neuron"` — the presynaptic class
- **Downstream neuron type**: e.g. `"mushroom body output neuron"`, `"descending neuron"` — the postsynaptic class
- **Weight threshold**: minimum synapse count per connection (default: `5` if not specified)
- **Group by class**: whether to aggregate results by neuron class rather than per individual neuron (default: `False`)
- **Data sources**: which connectome datasets to include or exclude. Run the dataset listing script (see Setup) to get the current list of available datasets with their symbols. The user can either specify datasets to **exclude** or datasets to **include** (from which you derive the exclude list). Default: exclude `hb` and `fafb`.

- **Query mode**: infer from user intent:

| Clues | Mode |
|---|---|
| "upstream of", "inputs to", "presynaptic to" | set `downstream_type` only |
| "downstream of", "outputs from", "postsynaptic to" | set `upstream_type` only |
| "between X and Y", "X → Y", "X to Y" | set both `upstream_type` and `downstream_type` |
| "all connections from X", "what does X connect to" | set `upstream_type` only |
| "summarise by class", "class level", "aggregated" | `group_by_class=True` |

At least one of `upstream_type` or `downstream_type` must be provided. If neither can be extracted, ask the user.

**Before running the query**, confirm the parameters with the user. Show them what you plan to use and let them adjust. For example:

> Here's what I'll query:
> - **Upstream type:** Kenyon cell
> - **Downstream type:** (any)
> - **Min. weight:** 5
> - **Group by class:** No (per-neuron results)
> - **Excluded DBs:** hb, fafb (Hemibrain & catmaid FAFB excluded)
>
> Shall I proceed, or would you like to change any of these?

**STOP and wait for the user's reply.** Only proceed to Step 2 after they confirm. If the user's original request already specifies all parameters explicitly, you may skip confirmation.

---

### Step 2: Resolve neuron type names (optional but recommended)

If the user uses informal or ambiguous neuron names, use the `mcp__virtual-fly-brain__search_terms` tool to validate and canonicalise the label before querying. This avoids silent failures when a label doesn't match VFB's controlled vocabulary.

Example: searching for `"Kenyon cell"` confirms the canonical label and short_form ID used in VFB.

If the VFB MCP search returns multiple candidates, show a brief disambiguation list and ask the user to confirm before proceeding.

If the name is already clearly canonical (e.g. `"GABAergic neuron"`, `"mushroom body output neuron"`), skip this step.

---

### Step 3: Execute the query

Run:

```bash
.venv/bin/python .claude/skills/vfb-connectivity/scripts/query_connectivity.py \
    --upstream "GABAergic neuron" \
    --downstream "mushroom body output neuron" \
    --weight 5 \
    --exclude-dbs hb fafb
```

**Arguments:**

| Argument | Required | Default | Description |
|---|---|---|---|
| `--upstream` | At least one of upstream/downstream | `None` | Upstream (presynaptic) neuron type label |
| `--downstream` | At least one of upstream/downstream | `None` | Downstream (postsynaptic) neuron type label |
| `--weight` | No | `5` | Minimum synapse count threshold |
| `--group-by-class` | No | off | Aggregate results by neuron class |
| `--exclude-dbs` | No | `hb fafb` | Databases to exclude; pass with no values to include all |

**Notes:**
- Omit `--upstream` or `--downstream` to leave that side unconstrained
- `--group-by-class` returns one row per class pair; without it, one row per neuron pair
- `--exclude-dbs` with no values (just the flag) includes all data sources

---

### Step 4: Handle results

**If connections found (per-neuron mode, `group_by_class=False`):**

DataFrame columns:
- `upstream_class`, `upstream_class_id` — class label(s) and ID(s) of the upstream neuron (pipe-separated if multiple)
- `upstream_neuron_id`, `upstream_neuron_name` — individual neuron
- `weight` — synapse count
- `downstream_neuron_id`, `downstream_neuron_name` — individual neuron
- `downstream_class`, `downstream_class_id` — class label(s) and ID(s) of downstream neuron
- `up_data_source`, `up_accession` — data source and accession for upstream neuron
- `down_data_source`, `down_accession` — data source and accession for downstream neuron

Present a summary table. If the result is large (>50 rows), show:
1. Total connection count
2. Top 20 rows sorted by `weight` descending
3. Summary stats: unique upstream neurons, unique downstream neurons, weight range

**If connections found (class mode, `group_by_class=True`):**

DataFrame columns:
- `upstream_class`, `upstream_class_id`
- `downstream_class`, `downstream_class_id`
- `total_upstream_count` — total neurons of upstream class in the dataset
- `connected_upstream_count` — how many actually connect to downstream class
- `percent_connected` — fraction connected
- `pairwise_connections` — total number of neuron-pair connections
- `total_weight` — summed synapse counts
- `average_weight` — mean synapses per connection

Present as a ranked table sorted by `pairwise_connections` descending.

**If zero results:**

Run a relaxation loop to diagnose:

1. Lower the weight threshold (try `weight=1`) → report count
2. Remove `exclude_dbs` filter (`exclude_dbs=[]`) → report count
3. Swap to `group_by_class=True` to check if class-level data exists → report count

Show the user what was tried and what each change produced. Let them decide which relaxation to apply.

**If error (returns `1`):**

Confirm with the user which neuron type(s) to use, then retry.

---

### Step 5: Output

Always include a **resolved terms block**:

```
Query:
- Upstream type:   GABAergic neuron
- Downstream type: (any)
- Min. weight:     5
- Excluded DBs:    hb, fafb
- Group by class:  No

Results: 42 connections across 18 upstream neurons → 31 downstream neurons
```

Then present the result table.

**Save option**: If the user asks to save results, write the already-captured DataFrame output directly to a CSV file using the `Write` tool — do **not** re-run the query. Save to `outputs/connectivity_{upstream}_{downstream}_{timestamp}.csv`.

---

### Step 6: Closing offer

After presenting results, offer relevant follow-up options:

- **Explore a specific neuron**: "To get full details on any neuron listed, I can look it up in VFB using its `short_form` ID."
- **Reverse the query**: "To find what connects *back* to [upstream_type], swap the upstream/downstream and re-run."
- **Class-level summary**: "To aggregate these results by neuron class, re-run with `group_by_class=True`."
- **Visualise in VFB**: "You can view any neuron directly at `https://v2.virtualflybrain.org/org.geppetto.frontend/geppetto?id=<short_form>`."

---

## Error paths

| Situation | Behaviour |
|-----------|-----------|
| `.venv` not found | Tell user to run `bash setup_venv.sh` first |
| Label not found in VFB | Use `mcp__virtual-fly-brain__search_terms` to suggest alternatives |
| Both types are `None` | Ask user to specify at least one neuron type |
| Empty DataFrame | Run relaxation loop (Step 4) |
| Connection timeout | Retry once; if it fails again, report the endpoint (`http://pdb.v4.virtualflybrain.org`) may be temporarily unavailable |

---

## Testing

Integration tests live in `tests/` and run against the live VFB knowledge graph using pytest:

```bash
.venv/bin/python -m pytest .claude/skills/vfb-connectivity/tests/ -v --rootdir=.claude/skills/vfb-connectivity
```

**After any change to the scripts or queries in this skill**, ask the user whether they'd like you to run the test suite before considering the change complete.

---

## Notes

- `query_by_label=True` is the correct default — VFB labels like `"Kenyon cell"` match the `rdfs:label` in the knowledge graph
- `exclude_dbs` accepts dataset symbols (from `list_datasets.py`); default is `['hb', 'fafb']` but always confirm with the user. If the user specifies datasets to **include**, derive the exclude list by subtracting from the full dataset list
- Class labels may be pipe-separated (e.g. `"Kenyon cell|γ Kenyon cell"`) when a neuron belongs to multiple classes — this is expected
- `weight` is a minimum threshold on the `r.weight[0]` property in the Neo4j graph (synapse count per connection)
