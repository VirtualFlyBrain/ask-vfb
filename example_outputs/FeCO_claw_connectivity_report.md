# FeCO Claw Neuron Connectivity Report

**Date:** 2026-03-10
**Tools used:** VFB MCP, vfb_connect Python library, OLS4 MCP, WebFetch (eLife)
**Primary reference:** Agrawal et al. 2020, *eLife* 9: e60299 (PMID 33263281, DOI 10.7554/eLife.60299)

---

## Methods & Steps

### Step 1 — Term discovery (VFB MCP: `search_terms`)

Query: `"chordotonal neuron claw"`, filtered to classes/neurons.

Top result: **femoral chordotonal claw neuron** (`FBbt_00049557`), synonym *FeCO claw neuron*. 10 results returned from 66 total; other hits included segment-specific subclasses and unrelated chordotonal types (Wheeler's organ, prosternal, larval).

### Step 2 — Class characterisation (VFB MCP: `get_term_info`)

Retrieved full term info for `FBbt_00049557`:

- Description sourced from Phillis et al. 1996 and Mamiya et al. 2018
- SuperTypes confirmed: Cholinergic, Sensory_neuron, Proprioceptive_system, Adult
- Relationships: `has sensory dendrite in` → ventral scoloparium of FeCO; `has soma location` → femoral chordotonal organ
- 278 individual images available (MANC + BANC datasets)
- 11 subclasses identified via `SubclassesOf` query, including extension and flexion variants per thoracic segment
- Single expression pattern overlap: P{GMR73D10-GAL4} (FBrf0247582 = Agrawal et al. 2020)
- Example instances: MANC (SNpp41_ProLN/MesoLN/MetaLN) and BANC (720575941...) individuals

### Step 3 — Instance inspection (VFB MCP: `get_term_info` on `VFB_jrcv3m9u`)

Inspected representative instance **SNpp41_ProLN_R (MANC:168834)**:

- Comment from MANC: `"class-sensory neuron, subclass-prothoracic leg FeCO claw, systematic type-SNpp41"`
- Tags: Cholinergic, Glutamatergic (dual NT annotation in MANC)
- Part of: adult ventral nerve cord, male organism
- `NeuronNeuronConnectivityQuery` count = 0 for this individual (connectivity stored at population level)
- `NeuronInputsTo` also empty — confirmed that type-level queries are needed

### Step 4 — Type-level downstream connectivity (`vfb_connect`: `get_connected_neurons_by_type`)

```python
from vfb_connect import vfb
results = vfb.get_connected_neurons_by_type(
    upstream_type='femoral chordotonal claw neuron',
    weight=5,
    exclude_dbs=[]  # include MANC, BANC, FAFB
)
```

**Result:** 14,580 rows, 13 columns:
`upstream_class`, `upstream_class_id`, `upstream_neuron_id`, `upstream_neuron_name`, `weight`, `downstream_neuron_id`, `downstream_neuron_name`, `downstream_class`, `downstream_class_id`, `up_data_source`, `up_accession`, `down_data_source`, `down_accession`

Aggregated by `downstream_class` + `downstream_class_id`, sorted by `total_weight`:
**934 unique downstream classes** identified.

### Step 5 — Motor neuron filtering

Filtered `downstream_class` for `'motor'` (case-insensitive):

```python
motor = results[results['downstream_class'].str.contains('motor', case=False, na=False)]
```

Identified direct connections to tibial levator and depressor motor neurons across all three thoracic segments, plus pleural remotor and dorsal prothoracic nerve motor neurons.

Filtered for `'ascending'`: only 22 weight total — negligible ascending output.

### Step 6 — Interneuron name lookup (`vfb_connect`: `lookup_name`)

Resolved top interneuron FBbt IDs to short labels:

| FBbt ID | Short name |
|---|---|
| FBbt_20010382 | IN19A060 |
| FBbt_20010376 | IN19A054 |
| FBbt_20010363 | IN19A041 |
| FBbt_20010481 | IN19B035 |
| FBbt_20010400 | IN19A081 |
| FBbt_20009973 | IN14A018 |
| FBbt_20009425 | IN08B054 |

### Step 7 — Literature retrieval (WebFetch → eLife)

Fetched `https://elifesciences.org/articles/60299` with two separate prompts targeting:
1. FeCO subtype morphology, encoding, downstream interneurons, motor connections, GCaMP data
2. GMR73D10-GAL4, extension/flexion subtype anatomy, VNC neuropil regions, monosynaptic reflex evidence, behavioural results

Key content extracted (see findings below). Note: artl-mcp (Europe PMC) was not available in this session as the server was not active; WebFetch was used as fallback. For future sessions, `artl-mcp` should be used for full-text retrieval.

### Step 8 — Subtype ontology lookup (VFB MCP: `get_term_info` on `FBbt_00053523`)

Fetched prothoracic claw extension neuron to verify subtype hierarchy:
confirmed `Types`: femoral chordotonal claw extension neuron (`FBbt_00053520`) + prothoracic femoral chordotonal claw neuron (`FBbt_00049560`).
No images or expression patterns currently linked to this subtype.

---

## Findings

### 1. The FeCO and its three parallel channels

The femoral chordotonal organ (FeCO) contains **152 neurons** organised into three morphologically and functionally distinct subtypes (Mamiya et al. 2018; Agrawal et al. 2020):

| Subtype | Encodes | Primary downstream interneuron | NT of interneuron |
|---|---|---|---|
| **Claw** | Tibial **position** (static joint angle) | 13Bα | GABAergic |
| **Hook** | Tibial **movement direction** (flexion or extension) | 9Aα | GABAergic |
| **Club** | Tibial **vibration** + bidirectional movement | 10Bα | Cholinergic |

Each sensory subtype maps onto a distinct hemilineage-defined interneuron population — a parallel-channel architecture for proprioceptive coding.

### 2. Claw neuron morphology

- **Soma**: blade-shaped strip along the long axis of the femur
- **Dendrites**: ventral scoloparium of the femoral chordotonal organ
- **Axon**: enters the VNC and splits into **three branches** — one projecting medially (following the club neuron trajectory), one dorsally, one anteriorly — giving the characteristic claw appearance (Phillis et al. 1996; Mamiya et al. 2018)
- **Neurotransmitter**: cholinergic (with glutamatergic co-annotation in some MANC instances, likely reflecting dual-transmitter labelling in the EM dataset)

### 3. Functional encoding

- Respond to **static tibial position** — tonic activity that tracks joint angle continuously throughout the flexion–extension range
- Do **not** respond to vibration, distinguishing them from club neurons
- Two tuning subtypes (reflected in VFB ontology):
  - **Extension-tuned** ([FBbt_00053520](https://v2.virtualflybrain.org/org.geppetto.frontend/geppetto?id=FBbt_00053520)): active when tibia is extended
  - **Flexion-tuned** ([FBbt_00053527](https://v2.virtualflybrain.org/org.geppetto.frontend/geppetto?id=FBbt_00053527)): active when tibia is flexed
- T1/T2/T3 segment-specific subclasses exist for each: 11 subclasses total in VFB

### 4. Primary downstream circuit: 13Bα interneurons

The first-order interneurons receiving claw input are the **13Bα neurons** (13B hemilineage, GABAergic):

- **Tuning matches claw neurons**: tonic calcium increase during tibia extension, decrease during flexion; insensitive to vibration (Agrawal 2020, Fig. 1)
- **Graded (non-spiking) coding**: membrane potential provides a linear, continuous readout of joint angle; no detectable action potentials
- **Low heterogeneity** across individual cells within a segment
- **Function**: "encode femur-tibia joint angle and mediate postural changes in tibia position" (Agrawal 2020)

In MANC connectome naming, **IN13B013** and **IN13B005** are instances of this population. The connectome data shows strong claw → IN13B connections (>4,000 combined weight).

> **Caveat noted by Agrawal 2020**: at the time of publication, direct monosynaptic input from claw neurons to 13Bα was inferred from anatomy and tuning, not directly demonstrated. The MANC connectome (Takemura et al. 2023) has since provided the synapse-resolution evidence.

### 5. Downstream connectivity — full landscape

From `get_connected_neurons_by_type` (weight ≥ 5, all datasets): **14,580 connections** across **934 downstream classes**, sourced from MANC and BANC connectomes.

#### Top interneuron targets (aggregated by class, sorted by total synaptic weight)

| Downstream class | Total weight | Upstream claw neurons | Downstream neurons | Datasets |
|---|---|---|---|---|
| IN13A002 (T1 + T2 + T3) | ~24,000 combined | 10–28 per segment | 1–6 | MANC |
| IN19A060 | 8,057 | 56 | 32 | BANC + MANC |
| IN19A054 | 4,019 | 40 | 11 | BANC + MANC |
| IN19A041 | 3,719 | 38 | 12 | BANC + MANC |
| IN19B035 | 3,314 | 27 | 6 | BANC + MANC |
| FeCO claw neuron (self) | 3,222 | 50 | 41 | BANC + MANC |
| IN13B013 (T2 + T3) | ~4,244 combined | 20–23 | 2 | MANC |
| IN08B054 | 1,877 | 20 | 12 | BANC + MANC |
| IN19A081 | 1,631 | 24 | 9 | BANC + MANC |
| IN14A018 | 1,446 | 19 | 10 | BANC + MANC |

#### Direct motor neuron connections (monosynaptic reflex arc)

| Motor neuron target | Total weight | Upstream claw neurons |
|---|---|---|
| Metathoracic tibial levator MN (T3) | 1,216 | 9 |
| Mesothoracic tibial levator MN (T2) | ~1,312 | 9–10 |
| Prothoracic tibial levator MN (T1) | 880 | 10 |
| Tibial depressor MN — T1 (prothoracic) | ~260 | 5 |
| Tibial depressor MN — T3 (metathoracic) | ~212 | 6 |
| Mesothoracic pleural remotor MN | 252 | 6 |
| Motor neuron of adult dorsal prothoracic nerve | 236 | 6 |

#### Ascending output

Only **~22 weight total** to ascending neuron classes — negligible. Processing is almost entirely local within the VNC.

### 6. Interpretation

**Monosynaptic resistance reflex**: The strongest motor output is to tibial levator motor neurons across all three leg segments. This constitutes a classic resistance reflex loop:

```
tibia extends → claw neurons (ACh) → tibial levator MN → tibia levator muscle → opposes extension
```

The depressor MN connections provide bidirectional joint stabilisation. Both pathways were inferred functionally by Agrawal 2020 and are now directly confirmed in the MANC connectome.

**Parallel interneuron processing**: The dominant interneuron target IN13A002 (>24,000 weight, present in all three segments separately) is leg-segment-specific and likely coordinates within-segment sensorimotor processing. The IN19A-series neurons (060, 054, 041, 081) receive convergent claw input from many upstream neurons across both MANC and BANC datasets, suggesting a role in cross-segmental or bilateral proprioceptive integration.

**Recurrent claw → claw connections**: 3,222 weight across 50 upstream neurons projecting to 41 other claw neurons. This suggests lateral inhibition or gain control within the proprioceptor population itself — a form of sensory processing before information even reaches interneurons.

**Graded coding for speed**: Walking Drosophila step at ~15 Hz; Agrawal 2020 notes VNC circuits must process proprioceptive signals within **~30 ms** between steps. The non-spiking, graded potential coding of 13Bα downstream neurons (and presumably the direct sensory→motor pathway) avoids spike-initiation delay and provides a continuous, low-latency joint angle signal.

### 7. Genetic access

- **GMR73D10-GAL4** labels FeCO claw neurons (Agrawal et al. 2020; VFB expression overlap `VFBexp_FBtp0062546`)
- No subtype-specific (extension vs. flexion) drivers are well established as of the paper

---

## Summary

FeCO claw neurons are cholinergic proprioceptors encoding static tibial joint angle. Their axons branch into a three-pronged "claw" morphology in the VNC and connect to:

1. **GABAergic 13Bα interneurons** (IN13B series in MANC) — graded, linear position encoding; mediate postural reflexes
2. **Tibial levator motor neurons** (all 3 segments) — monosynaptic resistance reflex, now confirmed by MANC
3. **Tibial depressor motor neurons** — bidirectional stabilisation
4. **Broadly connected VNC interneurons** (IN19A/B series, IN13A002) — cross-segmental integration
5. **Other claw neurons** — recurrent/lateral connections for gain control

The circuit architecture is consistent with a dedicated proprioceptive channel for joint position that drives both fast reflexive motor control and slower postural adjustment.

---

## Data sources

| Dataset | Reference | VFB prefix |
|---|---|---|
| MANC (Male Adult Nerve Cord) | Takemura et al. 2023 | VFB_jrcv... |
| BANC (Brain And Nerve Cord) | — | VFB_0010... |
| FlyBase ontology (FBbt) | flybase.org | FBbt_... |
| Agrawal et al. 2020 | eLife 9: e60299 | FBrf0247582 |
| Mamiya et al. 2018 | — | — |
| Phillis et al. 1996 | — | — |
