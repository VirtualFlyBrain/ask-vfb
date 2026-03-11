---
name: annotated-connectome
description: Generates circuit diagrams with functional hypotheses from VFB connectivity data. Pulls neuron connectivity from Virtual Fly Brain, adds neurotransmitter and receptor information from VFB and literature, then produces an interactive HTML circuit diagram with hypothesised functions. Use when the user asks about fly brain circuits, neuron connectivity, circuit function, or mentions VFB neurons.
argument-hint: "[neuron type or circuit region]"
allowed-tools: Bash, Read, Write, Edit, Glob, Grep, WebSearch, WebFetch, Agent
---

# Ask VFB: Circuit Diagram Generator

You are building a circuit diagram with functional hypotheses for Drosophila neurons/circuits.

## Workflow

### Setup

All Python commands use the .venv created by setup_venv.sh. Always prefix Python execution with:

source .venv/bin/activate && python - <<'EOF'
...code...
EOF

Or equivalently use .venv/bin/python directly:

.venv/bin/python -c "..."

Never use the system Python. If .venv is missing, tell the user to run bash setup_venv.sh first.

Step 1: Parse input

Extract from the user's request:

    Upstream neuron type: e.g. "GABAergic neuron", "Kenyon cell", "olfactory receptor neuron" — the presynaptic class
    Downstream neuron type: e.g. "mushroom body output neuron", "descending neuron" — the postsynaptic class
    Weight threshold: minimum synapse count per connection (default: 5 if not specified)
    Group by class: whether to aggregate results by neuron class rather than per individual neuron (default: False)
    Excluded databases: databases to exclude (default: ['hb', 'fafb'] — excludes Hemibrain and catmaid FAFB)
    Query mode: infer from user intent:

Clues 	Mode
"upstream of", "inputs to", "presynaptic to" 	set downstream_type only
"downstream of", "outputs from", "postsynaptic to" 	set upstream_type only
"between X and Y", "X → Y", "X to Y" 	set both upstream_type and downstream_type
"all connections from X", "what does X connect to" 	set upstream_type only
"summarise by class", "class level", "aggregated" 	group_by_class=True

At least one of upstream_type or downstream_type must be provided. If neither can be extracted, use AskUserQuestion to ask the user.
Step 2: Resolve neuron type names (optional but recommended)

If the user uses informal or ambiguous neuron names, use the mcp__virtual-fly-brain__search_terms tool to validate and canonicalise the label before querying. This avoids silent failures when a label doesn't match VFB's controlled vocabulary.

Example: searching for "Kenyon cell" confirms the canonical label and short_form ID used in VFB.

If the VFB MCP search returns multiple candidates, show a brief disambiguation list and ask the user to confirm before proceeding.

If the name is already clearly canonical (e.g. "GABAergic neuron", "mushroom body output neuron"), skip this step.
Step 3: Execute the query

Run via the .venv Python:

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

Parameter notes:

    Set unused type to None (not an empty string)
    query_by_label=True is always correct when passing neuron class labels
    group_by_class=False returns one row per neuron pair; group_by_class=True aggregates by class
    exclude_dbs accepts database short_form IDs or symbols; keep defaults unless user asks otherwise

Step 4: Handle results

If connections found (per-neuron mode, group_by_class=False):

DataFrame columns:

    upstream_class, upstream_class_id — class label(s) and ID(s) of the upstream neuron (pipe-separated if multiple)
    upstream_neuron_id, upstream_neuron_name — individual neuron
    weight — synapse count
    downstream_neuron_id, downstream_neuron_name — individual neuron
    downstream_class, downstream_class_id — class label(s) and ID(s) of downstream neuron
    up_data_source, up_accession — data source and accession for upstream neuron
    down_data_source, down_accession — data source and accession for downstream neuron


### Step 2: Gather data in parallel

Spawn **three agents in parallel**:

**Agent 1 — Connectivity & Neurotransmitters (VFB)**
- For each neuron of interest, call `virtual-fly-brain:get_term_info` to retrieve:
  - Upstream and downstream connectivity (synapse counts, partner neurons)
  - Neurotransmitter predictions (from connectome data where available)
  - Classification and anatomical region
- Call `virtual-fly-brain:run_query` for NBLAST similarity if morphological context is useful
- Record: `neuron_id`, `neuron_name`, `neurotransmitter`, `upstream_partners[]`, `downstream_partners[]`, `synapse_counts`, `brain_region`

**Agent 2 — Literature: Neurotransmitters, Receptors & Function**
- Web search for each neuron type + "neurotransmitter", "receptor", "function", "Drosophila"
- Key sources to check:
  - FlyBase gene expression data
  - Published connectome papers (Scheffer et al., Dorkenwald et al., Schlegel et al.)
  - scRNAseq studies for receptor expression (e.g., Davie et al. 2018, Li et al. 2022)
- Record: `neurotransmitter` (confirmed vs predicted), `receptors_expressed[]`, `known_function`, `citations[]`

**Agent 3 — Anatomical Context**
- Use `virtual-fly-brain:get_term_info` on the brain regions involved
- Web search for functional role of the circuit/neuropil region
- Record: `region_name`, `region_function`, `known_circuit_roles[]`

### Step 3: Synthesize

Merge the three agents' results:
1. Build a node list (neurons) with properties: name, type, neurotransmitter, receptors, brain region
2. Build an edge list (connections) with: source, target, synapse count, neurotransmitter, sign (excitatory/inhibitory)
3. Determine sign from neurotransmitter:
   - **Excitatory**: acetylcholine (nAChR), glutamate (varies — check receptor subtype)
   - **Inhibitory**: GABA (Rdl, GABA-B), glutamate (GluCl)
   - **Modulatory**: serotonin, dopamine, octopamine, tyramine
4. Formulate functional hypotheses based on:
   - Circuit topology (feedforward, feedback, lateral inhibition, recurrent)
   - Known functions of component neurons from literature
   - Neurotransmitter/receptor combinations and their known effects

### Step 4: Generate circuit diagram

Write the synthesised data as JSON, then run the bundled script:

```bash
python ${CLAUDE_SKILL_DIR}/scripts/circuit_diagram.py circuit_data.json
```

This generates `circuit_diagram.html` and opens it in the browser.

If the script fails or is unavailable, generate the circuit diagram directly as an HTML file with inline SVG/JavaScript.

### Step 5: Present results

Summarise:
1. **Circuit overview**: what neurons are involved and how they connect
2. **Neurotransmitter map**: what each neuron releases and what receptors its targets express
3. **Functional hypotheses**: what the circuit likely computes, with reasoning
4. **Confidence levels**: flag which data is confirmed vs predicted vs hypothesised
5. **Citations**: list key papers supporting the analysis

## Data format for circuit_data.json

```json
{
  "title": "Circuit name/description",
  "neurons": [
    {
      "id": "vfb_id",
      "name": "Neuron name",
      "type": "sensory|interneuron|motor|modulatory",
      "neurotransmitter": "acetylcholine",
      "nt_evidence": "connectome_prediction|literature|scRNAseq",
      "receptors": ["nAChR-alpha7", "Rdl"],
      "brain_region": "region name",
      "known_function": "brief description or null"
    }
  ],
  "connections": [
    {
      "source": "vfb_id_1",
      "target": "vfb_id_2",
      "synapse_count": 125,
      "neurotransmitter": "acetylcholine",
      "sign": "excitatory",
      "sign_evidence": "receptor_based|nt_based|literature"
    }
  ],
  "hypotheses": [
    {
      "description": "This circuit implements lateral inhibition for...",
      "confidence": "high|medium|low",
      "supporting_evidence": ["citation1", "citation2"]
    }
  ],
  "citations": [
    {
      "key": "Scheffer2020",
      "text": "Scheffer et al. (2020) A connectome and analysis..."
    }
  ]
}
```
