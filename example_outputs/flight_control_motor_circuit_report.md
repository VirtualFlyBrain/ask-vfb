# Flight Control Muscle Motor Circuit in *Drosophila*

**Date:** 2026-03-17
**Data sources:** VFB ontology (FBbt), MANC connectome (Takemura et al. 2023), Berg et al. 2025 (MaleCNS)
**Methods:** VFB ontology cypher queries; `vfb_connect.get_neurons_upstream_of()` on MANC instances

---

## 1. Flight Control Muscles and Their Motor Neurons

VFB ontology ([FBbt_00052767](https://v2.virtualflybrain.org/org.geppetto.frontend/geppetto?id=FBbt_00052767)) defines the **flight control muscle** class with the following subclasses and their dedicated motor neurons:

| Muscle | Motor Neuron | MN VFB Link |
|---|---|---|
| Direct flight muscle | direct flight muscle motor neuron | [FBbt_00004065](https://v2.virtualflybrain.org/org.geppetto.frontend/geppetto?id=FBbt_00004065) |
| Tergopleural muscle 1 | dorsal tp motor neuron | [FBbt_00004071](https://v2.virtualflybrain.org/org.geppetto.frontend/geppetto?id=FBbt_00004071) |
| Tergopleural muscle 2 | ventral tp motor neuron | [FBbt_00004072](https://v2.virtualflybrain.org/org.geppetto.frontend/geppetto?id=FBbt_00004072) |
| Tergopleural muscle 2 | tpn motor neuron | [FBbt_00048110](https://v2.virtualflybrain.org/org.geppetto.frontend/geppetto?id=FBbt_00048110) |
| Mesothoracic tergotrochanter muscle | TTMn (mesothoracic tergotrochanter muscle motor neuron) | [FBbt_00007406](https://v2.virtualflybrain.org/org.geppetto.frontend/geppetto?id=FBbt_00007406) |
| Mesothoracic tergotrochanter muscle | satellite tergotrochanter muscle motor neuron | [FBbt_00053058](https://v2.virtualflybrain.org/org.geppetto.frontend/geppetto?id=FBbt_00053058) |
| Mesothoracic pleurosternal muscle 59 | ps1 motor neuron | [FBbt_00047248](https://v2.virtualflybrain.org/org.geppetto.frontend/geppetto?id=FBbt_00047248) |
| Mesothoracic pleurosternal muscle 60 | ps2 motor neuron | [FBbt_00052729](https://v2.virtualflybrain.org/org.geppetto.frontend/geppetto?id=FBbt_00052729) |
| Wing axillary muscle I1 | wing axillary muscle I1 motor neuron | [FBbt_00004070](https://v2.virtualflybrain.org/org.geppetto.frontend/geppetto?id=FBbt_00004070) |
| Wing axillary muscle I2 | wing axillary muscle I2 motor neuron | [FBbt_00048109](https://v2.virtualflybrain.org/org.geppetto.frontend/geppetto?id=FBbt_00048109) |
| Wing axillary muscle III1 | wing axillary muscle III1 motor neuron | [FBbt_00004069](https://v2.virtualflybrain.org/org.geppetto.frontend/geppetto?id=FBbt_00004069) |
| Wing axillary muscle III3 | wing axillary muscle III3 motor neuron | [FBbt_00004067](https://v2.virtualflybrain.org/org.geppetto.frontend/geppetto?id=FBbt_00004067) |
| Wing axillary muscle III4 | wing axillary muscle III4 motor neuron | [FBbt_00052726](https://v2.virtualflybrain.org/org.geppetto.frontend/geppetto?id=FBbt_00052726) |
| Wing axillary muscle hg1 | wing axillary muscle hg1 motor neuron | [FBbt_00047246](https://v2.virtualflybrain.org/org.geppetto.frontend/geppetto?id=FBbt_00047246) |
| Wing axillary muscle hg2 | wing axillary muscle hg2 motor neuron | [FBbt_00048111](https://v2.virtualflybrain.org/org.geppetto.frontend/geppetto?id=FBbt_00048111) |
| Wing axillary muscle hg3 | wing axillary muscle hg3 motor neuron | [FBbt_00052727](https://v2.virtualflybrain.org/org.geppetto.frontend/geppetto?id=FBbt_00052727) |
| Wing axillary muscle hg4 | wing axillary muscle hg4 motor neuron | [FBbt_00052728](https://v2.virtualflybrain.org/org.geppetto.frontend/geppetto?id=FBbt_00052728) |
| Wing basalar muscle b1 | wing basalar muscle b1 motor neuron | [FBbt_00004066](https://v2.virtualflybrain.org/org.geppetto.frontend/geppetto?id=FBbt_00004066) |
| Wing basalar muscle b2 | wing basalar muscle b2 motor neuron | [FBbt_00004068](https://v2.virtualflybrain.org/org.geppetto.frontend/geppetto?id=FBbt_00004068) |
| Wing basalar muscle b3 | wing basalar muscle b3 motor neuron | [FBbt_00052725](https://v2.virtualflybrain.org/org.geppetto.frontend/geppetto?id=FBbt_00052725) |

All connections are `sends_synaptic_output_to_cell` (NMJ) assertions in FBbt.

---

## 2. Ontology-Level Upstream Inputs to Flight Control Motor Neurons

Querying VFB ontology class-level assertions for inputs to the 21 motor neurons above revealed only **two recorded presynaptic neurons**:

### 2a. Giant fiber neuron → TTMn (electrical synapse)

The **giant fiber neuron** ([FBbt_00004020](https://v2.virtualflybrain.org/org.geppetto.frontend/geppetto?id=FBbt_00004020)) is connected to the mesothoracic tergotrochanter muscle motor neuron (TTMn) via an **electrical synapse** (`electrically_synapsed_to`).

The giant fiber is classified in VFB as:

- `adult descending neuron`
- `adult subesophageal sensory interneuron`
- `auditory system neuron`
- `mechanosensory system neuron`
- `sensory system neuron`

This is the canonical **giant fiber (GF) escape circuit**: the GF integrates visual and mechanosensory inputs and drives rapid escape flight initiation via a direct electrical synapse to the TTMn, which contracts the tergotrochanter for the take-off jump. The ultra-fast electrical coupling minimises synaptic delay.

### 2b. TN1A → hg1 motor neuron (chemical synapse)

The **adult doublesex TN1A (male) neuron** ([FBbt_00048100](https://v2.virtualflybrain.org/org.geppetto.frontend/geppetto?id=FBbt_00048100)) sends a chemical synapse to the wing axillary muscle hg1 motor neuron. TN1A is classified as:

- `adult interneuron` / `adult premotor neuron`
- `adult VNC neuron`
- `sexually-dimorphic neuron` / `adult doublesex neuron`
- **NOT sensory**

TN1A is a male-specific circuit element, likely involved in courtship or sex-specific flight modulation.

---

## 3. Connectomics: Upstream Inputs from MANC EM Dataset

Querying `vfb_connect.get_neurons_upstream_of()` (weight ≥ 5 synapses) on **12 MANC instances** of 9 flight control MN classes (Takemura et al. 2023):

| Motor Neuron | MANC ID | Upstream connections |
|---|---|---|
| TTMn | MANC:10068 | 81 |
| dorsal tp MN | MANC:10521 | 324 |
| ventral tp MN | MANC:10270 | 378 |
| tpn MN | MANC:10543 | 250 |
| ps1 MN | MANC:10958 | 441 |
| ps2 MN | MANC:11054 | 399 |
| satellite TTMn | MANC:17316 | 169 |
| axillary I1 MN | MANC:10225 | 392 |
| axillary hg1 MN | MANC:10011 | 443 |
| basalar b1 MN | MANC:10013 | 315 |
| DLM MN (b3) | MANC:10064 | 410 |
| DLM MN (iii1) | MANC:10287 | 203 |
| **Total** | | **3,805** |

**Note:** Berg et al. 2025 (MaleCNS) instances were also identified but lack connectivity data in VFB at present.

### Top upstream interneuron classes (by total synaptic weight)

These are all VNC interneurons (MANC `IN` naming convention):

| Interneuron class | Total weight | Connections |
|---|---|---|
| IN17A029 | 3,588 | 25 |
| IN19B072 | 2,796 | 36 |
| IN03B057 | 2,591 | 49 |
| IN03B063 | 2,526 | 51 |
| IN06A023 | 2,214 | 60 |
| IN06B052 | 1,874 | 32 |
| IN17A007 | 1,776 | 13 |
| IN10B001 | 1,680 | 12 |
| IN08A018 | 1,497 | 39 |
| IN17A026 | 1,492 | 21 |

> **Note on `AN` neurons:** 134 unique neurons with the `AN` prefix appear in the upstream data. These are **VNC interneurons** (confirmed by VFB tags: `adult VNC neuron`, no `Sensory_neuron` tag), not afferents, despite the prefix.

---

## 4. Direct Sensory Input to Flight Control Motor Neurons

### Are any upstream neurons sensory?

**Yes.** Neurons with `SN` and `SA` MANC prefixes are tagged `Sensory_neuron` in VFB and classified as sensory neurons of **wing** and **haltere campaniform sensilla**.

**338 direct sensory synaptic connections** from **275 unique sensory neurons** were identified.

### Sensory neuron types (by total weight)

| Sensory type | Nerve | Organ | Connections | Total weight |
|---|---|---|---|---|
| SNpp05 | ADMN | Wing campaniform sensillum | 50 | 1,329 |
| SApp04 | ADMN | Wing campaniform sensillum | 38 | 878 |
| SApp21 | DMetaN | Haltere campaniform sensillum | 34 | 648 |
| SApp* | DMetaN | Haltere campaniform sensillum | 42 | 622 |
| SApp19 | DMetaN | Haltere campaniform sensillum | 19 | 368 |
| SNpp03 | ADMN | Wing campaniform sensillum | 14 | 322 |
| SNpp32 | DMetaN | Haltere campaniform sensillum | 16 | 321 |
| SApp31 | DMetaN | Haltere campaniform sensillum | 18 | 265 |
| SNpp07 | ADMN | Wing campaniform sensillum | 12 | 262 |
| SNpp22 | DMetaN | Haltere campaniform sensillum | 14 | 217 |

**ADMN** = anterodorsal mesothoracic nerve (wing CS afferents)
**DMetaN** = dorsal mesothoracic nerve (haltere CS afferents)

All confirmed as **cholinergic** and tagged `Mechanosensory_system` in VFB.

### Sensory input per motor neuron

| Motor Neuron | Sensory connections | Total weight | Wing CS | Haltere CS |
|---|---|---|---|---|
| basalar b1 MN | 68 | **1,723** | 68 | 39 |
| DLM MN (b3) | 53 | 1,048 | 53 | 39 |
| DLM MN (iii1) | 42 | 807 | 41 | 25 |
| axillary I1 MN | 43 | 695 | 43 | 29 |
| axillary hg1 MN | 37 | 540 | 37 | 31 |
| tpn MN | 25 | 575 | 25 | 5 |
| ps2 MN | 23 | 382 | 22 | 1 |
| ps1 MN | 18 | 303 | 17 | 9 |
| dorsal tp MN | 14 | 185 | 14 | 14 |
| ventral tp MN | 12 | 96 | 10 | 3 |
| satellite TTMn | 3 | 19 | 3 | 0 |
| **TTMn** | **0** | **0** | — | — |

---

## 5. Summary and Biological Interpretation

### Circuit architecture

```
Wing campaniform sensilla (ADMN) ─────────────────────────────────────┐
Haltere campaniform sensilla (DMetaN) ────────────────────────────────┤
                                                                       ▼
Giant fiber (visual/mechanosensory) ──[electrical]──► TTMn ──► Tergotrochanter muscle
                                                                (escape jump)
TN1A (male-specific interneuron) ──────────────────► hg1 MN ──► Axillary hg1 muscle

VNC interneurons (IN*) ───────────────────────────► All flight control MNs
```

### Key findings

1. **Direct sensory→motor connections exist.** Wing and haltere campaniform sensilla neurons provide direct monosynaptic input to 11 of the 12 flight control motor neurons queried. This bypasses interneurons entirely and provides ultra-fast proprioceptive feedback during flight.

2. **Campaniform sensilla are the dominant direct sensory input.** Both wing (ADMN-projecting) and haltere (DMetaN-projecting) CS neurons contribute, consistent with their known roles in flight stabilisation: wing CS detect local wing loading during flapping; haltere CS detect Coriolis forces encoding body rotation.

3. **The basalar b1 and DLM motor neurons receive the heaviest sensory drive** (total weights of 1,723 and 1,048 respectively). These muscles are key regulators of wing stroke amplitude and power output.

4. **The TTMn (escape motor neuron) receives no direct campaniform input** at the ≥5 synapse threshold. This is consistent with its specialised role in the GF-driven escape circuit rather than in steady-state flight stabilisation. Its primary presynaptic input is the giant fiber via electrical synapse.

5. **The GF escape circuit is preserved at the ontology level** with an electrical synapse between the GF (a subesophageal sensory interneuron receiving auditory/mechanosensory input) and the TTMn — a well-characterised fast reflex arc.

6. **VNC interneurons (IN* classes) dominate the upstream input** in terms of connection numbers, representing premotor populations that likely integrate descending commands with sensory feedback before driving motor output.

---

## References / Data Sources

- Takemura S et al. (2023) A connectome of the *Drosophila* central complex. *Nat. Neurosci.* — MANC dataset
- Berg S et al. (2025) MaleCNS dataset (Berg2025) — full male CNS connectome
- FlyBase anatomy ontology (FBbt) via Virtual Fly Brain: [virtualflybrain.org](https://virtualflybrain.org)
- VFB IDs linked throughout; browse at `https://v2.virtualflybrain.org/org.geppetto.frontend/geppetto?id=<ID>`
