---
name: vfb-connectivity
description: Query synaptic connectivity between Drosophila neuron classes using VFB — supports upstream/downstream filtering, weight thresholds, and class-level aggregation. DO NOT USE FOR FINDING CONNECTIONS ON INDIVIDUAL NEURONS OR FOR CONNECTIONS BETWEEN MUSCLES & NEURONS OR SENSE ORGANS AND NEURONS.
user-invocable: true
---

# VFB Neuron Connectivity Query

Query synaptic connections between Drosophila neuron types using `vfb_connect.get_connected_neurons_by_type`. Returns per-neuron or class-aggregated connectivity data from the VirtualFlyBrain knowledge graph.

---

## Setup

All Python commands use the `.venv` created by `setup_venv.sh`. Always prefix Python execution with:

```bash
source .venv/bin/activate && python - <<'EOF'
...code...
EOF
```

Or equivalently use `.venv/bin/python` directly:

```bash
.venv/bin/python -c "..."
```

**Never use the system Python.** If `.venv` is missing, tell the user to run `bash setup_venv.sh` first.

---

## Instructions

### Step 1: Parse input

Extract from the user's request:

- **Upstream neuron type**: e.g. `"GABAergic neuron"`, `"Kenyon cell"`, `"olfactory receptor neuron"` — the presynaptic class
- **Downstream neuron type**: e.g. `"mushroom body output neuron"`, `"descending neuron"` — the postsynaptic class
- **Weight threshold**: minimum synapse count per connection (default: `5` if not specified)
- **Group by class**: whether to aggregate results by neuron class rather than per individual neuron (default: `False`)
- **Excluded databases**: databases to exclude (default: `['hb', 'fafb']` — excludes Hemibrain and catmaid FAFB)
- **Query mode**: infer from user intent:

| Clues | Mode |
|---|---|
| "upstream of", "inputs to", "presynaptic to" | set `downstream_type` only |
| "downstream of", "outputs from", "postsynaptic to" | set `upstream_type` only |
| "between X and Y", "X → Y", "X to Y" | set both `upstream_type` and `downstream_type` |
| "all connections from X", "what does X connect to" | set `upstream_type` only |
| "summarise by class", "class level", "aggregated" | `group_by_class=True` |

At least one of `upstream_type` or `downstream_type` must be provided. If neither can be extracted, use `AskUserQuestion` to ask the user.

---

### Step 2: Resolve neuron type names (optional but recommended)

If the user uses informal or ambiguous neuron names, use the `mcp__virtual-fly-brain__search_terms` tool to validate and canonicalise the label before querying. This avoids silent failures when a label doesn't match VFB's controlled vocabulary.

Example: searching for `"Kenyon cell"` confirms the canonical label and short_form ID used in VFB.

If the VFB MCP search returns multiple candidates, show a brief disambiguation list and ask the user to confirm before proceeding.

If the name is already clearly canonical (e.g. `"GABAergic neuron"`, `"mushroom body output neuron"`), skip this step.

---

### Step 3: Execute the query

Run via the `.venv` Python:

```bash
source .venv/bin/activate && python - <<'EOF'
import pandas as pd
from vfb_connect.cross_server_tools import VfbConnect

vfb = VfbConnect()

df = vfb.get_connected_neurons_by_type(
    weight=5,                        # replace with parsed weight
    upstream_type="GABAergic neuron",  # replace or set to None
    downstream_type=None,              # replace or set to None
    query_by_label=True,
    group_by_class=False,
    exclude_dbs=['hb', 'fafb'],
    return_dataframe=True
)

if isinstance(df, int):
    print("ERROR: at least one of upstream_type or downstream_type must be specified")
elif df is None or (hasattr(df, '__len__') and len(df) == 0):
    print("No connections found.")
else:
    print(f"{len(df)} connections found")
    print(df.to_string(index=False))
EOF
```

**Parameter notes:**
- Set unused type to `None` (not an empty string)
- `query_by_label=True` is always correct when passing neuron class labels
- `group_by_class=False` returns one row per neuron pair; `group_by_class=True` aggregates by class
- `exclude_dbs` accepts database `short_form` IDs or symbols; keep defaults unless user asks otherwise

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

**Save option**: If the user asks to save results, write to `outputs/connectivity_{upstream}_{downstream}_{timestamp}.csv` using:

```python
import datetime, os
os.makedirs("outputs", exist_ok=True)
timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
df.to_csv(f"outputs/connectivity_{timestamp}.csv", index=False)
print("Saved.")
```

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

## Notes

- `query_by_label=True` is the correct default — VFB labels like `"Kenyon cell"` match the `rdfs:label` in the knowledge graph
- The `exclude_dbs` default (`['hb', 'fafb']`) removes Hemibrain and catmaid FAFB datasets; pass `[]` to include all sources
- Class labels may be pipe-separated (e.g. `"Kenyon cell|γ Kenyon cell"`) when a neuron belongs to multiple classes — this is expected
- `weight` is a minimum threshold on the `r.weight[0]` property in the Neo4j graph (synapse count per connection)
