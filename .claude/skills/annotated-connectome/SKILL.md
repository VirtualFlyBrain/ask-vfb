---
name: ask-vfb
description: Generates circuit diagrams with functional hypotheses from VFB connectivity data. Pulls neuron connectivity from Virtual Fly Brain, adds neurotransmitter and receptor information from VFB and literature, then produces an interactive HTML circuit diagram with hypothesised functions. Use when the user asks about fly brain circuits, neuron connectivity, circuit function, or mentions VFB neurons.
argument-hint: "[neuron type or circuit region]"
allowed-tools: Bash, Read, Write, Edit, Glob, Grep, WebSearch, WebFetch, Agent
---

# Ask VFB: Circuit Diagram Generator

You are building a circuit diagram with functional hypotheses for Drosophila neurons/circuits.

## Workflow

### Step 1: Identify the target neurons

Use `virtual-fly-brain:search_terms` to find neurons matching the user's query. If the user provides VFB IDs directly, skip to Step 2.

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
