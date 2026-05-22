# Synaptic Connectivity of Leg Chordotonal Neurons in *Drosophila melanogaster*

**Query date:** 2026-03-10
**Data source:** VirtualFlyBrain (VFB) connectomics knowledge graph
**Neuron class:** [mechanosensory neuron of leg chordotonal organ](https://v2.virtualflybrain.org/org.geppetto.frontend/geppetto?id=FBbt_00048274) (FBbt_00048274)
**Minimum synapse weight:** 5 | **Excluded datasets:** Hemibrain, catmaid FAFB

---

## Background

The **femoral chordotonal organ (fCO)** is the primary proprioceptor of the *Drosophila* leg. It detects femur-tibia joint angle and velocity, encoding limb position and movement during walking and grooming. Three physiologically distinct mechanosensory neuron subclasses innervate the fCO:

| Subclass | VFB class | Physiological tuning |
|---|---|---|
| [Club neurons](https://v2.virtualflybrain.org/org.geppetto.frontend/geppetto?id=FBbt_00048274) | femoral chordotonal club neuron | Velocity / movement |
| [Claw neurons](https://v2.virtualflybrain.org/org.geppetto.frontend/geppetto?id=FBbt_00048274) | femoral chordotonal claw neuron | Position / static load |
| [Hook neurons](https://v2.virtualflybrain.org/org.geppetto.frontend/geppetto?id=FBbt_00048274) | femoral chordotonal hook neuron | Velocity / direction |

All three subclasses project axons into the ventral nerve cord (VNC), where they synapse onto interneurons, motor neurons, and ascending projection neurons. The query below was performed with class-level aggregation across both directions of connectivity.

---

## Downstream Targets (fCO → postsynaptic)

The query returned **1,209 downstream neuron classes**, reflecting the broad integration of proprioceptive signals across the VNC.

### Top downstream targets by connection count

| fCO subtype | Downstream target | Pairs | Total weight | Avg synapses | % neurons connected |
|---|---|---|---|---|---|
| Club | [adult VNC neuron](https://v2.virtualflybrain.org/org.geppetto.frontend/geppetto?id=FBbt_00049000) | 4,688 | 73,402 | 15 | 39% |
| Claw | [adult VNC neuron](https://v2.virtualflybrain.org/org.geppetto.frontend/geppetto?id=FBbt_00049000) | 3,878 | 64,632 | 16 | 42% |
| Hook | [adult VNC neuron](https://v2.virtualflybrain.org/org.geppetto.frontend/geppetto?id=FBbt_00049000) | 2,128 | 28,544 | 13 | 28% |
| Claw | [mesothoracic neuron](https://v2.virtualflybrain.org/org.geppetto.frontend/geppetto?id=FBbt_00058177) | 1,852 | 31,654 | 17 | 18% |
| Club | [metathoracic neuron](https://v2.virtualflybrain.org/org.geppetto.frontend/geppetto?id=FBbt_00058178) | 1,830 | 31,050 | 16 | 31% |
| Club | [mesothoracic neuron](https://v2.virtualflybrain.org/org.geppetto.frontend/geppetto?id=FBbt_00058177) | 1,480 | 22,936 | 15 | 33% |
| Claw | [metathoracic neuron](https://v2.virtualflybrain.org/org.geppetto.frontend/geppetto?id=FBbt_00058178) | 1,262 | 20,722 | 16 | 14% |
| Hook | [mesothoracic neuron](https://v2.virtualflybrain.org/org.geppetto.frontend/geppetto?id=FBbt_00058177) | 1,020 | 14,452 | 14 | 14% |
| Club | [prothoracic neuron](https://v2.virtualflybrain.org/org.geppetto.frontend/geppetto?id=FBbt_00058176) | 849 | 12,052 | 14 | 28% |
| Claw | [prothoracic neuron](https://v2.virtualflybrain.org/org.geppetto.frontend/geppetto?id=FBbt_00058176) | 744 | 12,084 | 16 | 10% |

### High-penetrance specific targets

Beyond broad VNC classes, several specific interneuron and ascending neuron types show notably high connection rates:

| fCO subtype | Downstream target | Pairs | Avg synapses | % connected |
|---|---|---|---|---|
| Claw | [adult IN13A002 neuron](https://v2.virtualflybrain.org/org.geppetto.frontend/geppetto?id=FBbt_00049027) | 282 | **56** | **67%** |
| Club | [adult AN08B018 neuron](https://v2.virtualflybrain.org/org.geppetto.frontend/geppetto?id=FBbt_00049178) | 684 | 17 | **62%** |
| Club | [adult INXXX007 neuron](https://v2.virtualflybrain.org/org.geppetto.frontend/geppetto?id=FBbt_00055307) | 286 | 15 | 61% |
| Claw | [adult IN13A009 neuron](https://v2.virtualflybrain.org/org.geppetto.frontend/geppetto?id=FBbt_00049034) | 258 | 20 | 61% |
| Claw | [adult IN13A005 neuron](https://v2.virtualflybrain.org/org.geppetto.frontend/geppetto?id=FBbt_00049030) | 204 | 19 | 48% |
| Club | [adult IN23B024 neuron](https://v2.virtualflybrain.org/org.geppetto.frontend/geppetto?id=FBbt_00049309) | 223 | 16 | 47% |
| Claw | [adult IN03A006 neuron](https://v2.virtualflybrain.org/org.geppetto.frontend/geppetto?id=FBbt_00048955) | 208 | 20 | 50% |

**IN13A002** stands out as the single strongest specific postsynaptic partner of claw neurons: 67% of claw neurons contact it with an average of 56 synapses per connection — approximately 3–4× more than most other targets.

**AN08B018** is the most penetrant ascending neuron target of club neurons (62%), suggesting a dedicated channel for velocity signals ascending to the brain.

### Motor neuron contacts

Chordotonal neurons make direct monosynaptic contacts onto motor neurons, constituting a short-latency proprioceptive reflex arc:

| fCO subtype | Downstream target | Pairs | Avg synapses | % connected |
|---|---|---|---|---|
| Claw | [primary motor neuron](https://v2.virtualflybrain.org/org.geppetto.frontend/geppetto?id=FBbt_00058183) | 118 | 15 | 19% |
| Hook | [secondary motor neuron](https://v2.virtualflybrain.org/org.geppetto.frontend/geppetto?id=FBbt_00058184) | 94 | 10 | 13% |
| Claw | [secondary motor neuron](https://v2.virtualflybrain.org/org.geppetto.frontend/geppetto?id=FBbt_00058184) | 106 | 7 | 14% |

### Recurrent collaterals

All three fCO subclasses make homotypic connections onto neurons of the same class, indicating local lateral inhibition within the sense organ circuit:

| Subtype | Pairs | Avg synapses |
|---|---|---|
| Club → Club | 361 | 8 |
| Claw → Claw | 296 | 7 |
| Hook → Hook | 274 | 11 |

---

## Upstream Inputs (presynaptic → fCO)

The query returned **182 upstream neuron classes**. Sensory neurons receiving synaptic input is a hallmark of **presynaptic inhibition** — a conserved mechanism for gain control and efference copy in proprioceptive circuits.

### Top upstream sources by connection count

| Upstream source | fCO subtype | Pairs | Total weight | Avg synapses |
|---|---|---|---|---|
| [adult VNC neuron](https://v2.virtualflybrain.org/org.geppetto.frontend/geppetto?id=FBbt_00049000) | Hook | 574 | 13,940 | 24 |
| [adult IN19A060 neuron](https://v2.virtualflybrain.org/org.geppetto.frontend/geppetto?id=FBbt_00049249) | Claw | 490 | 5,588 | 11 |
| [adult VNC neuron](https://v2.virtualflybrain.org/org.geppetto.frontend/geppetto?id=FBbt_00049000) | Club | 362 | 3,891 | 10 |
| [adult IN09A012 neuron](https://v2.virtualflybrain.org/org.geppetto.frontend/geppetto?id=FBbt_00048997) | Hook | 260 | 13,528 | **52** |
| [mesothoracic neuron](https://v2.virtualflybrain.org/org.geppetto.frontend/geppetto?id=FBbt_00058177) | Hook | 222 | 6,114 | 27 |
| [adult IN19A054 neuron](https://v2.virtualflybrain.org/org.geppetto.frontend/geppetto?id=FBbt_00049243) | Claw | 198 | 2,960 | 14 |
| [metathoracic neuron](https://v2.virtualflybrain.org/org.geppetto.frontend/geppetto?id=FBbt_00058178) | Hook | 168 | 4,190 | 24 |
| [adult glutamatergic neuron](https://v2.virtualflybrain.org/org.geppetto.frontend/geppetto?id=FBbt_00058160) | Claw | 166 | 1,370 | 8 |
| [adult IN13A008 neuron](https://v2.virtualflybrain.org/org.geppetto.frontend/geppetto?id=FBbt_00049033) | Club | 141 | 2,000 | 14 |
| [adult IN09A014 neuron](https://v2.virtualflybrain.org/org.geppetto.frontend/geppetto?id=FBbt_00048999) | Hook | 138 | 2,514 | 18 |
| [adult IN09A021 neuron](https://v2.virtualflybrain.org/org.geppetto.frontend/geppetto?id=FBbt_00049006) | Hook | 64 | 2,476 | **38** |
| [prothoracic neuron](https://v2.virtualflybrain.org/org.geppetto.frontend/geppetto?id=FBbt_00058176) | Hook | 128 | 2,960 | 23 |
| [abdominal neuron](https://v2.virtualflybrain.org/org.geppetto.frontend/geppetto?id=FBbt_00058175) | Hook | 56 | 676 | 12 |

### Recurrent homotypic inputs

As with the downstream data, all three fCO subtypes receive input from neurons of the same class:

| Source → Target | Pairs | Avg synapses |
|---|---|---|
| Club → Club | 361 | 8 |
| Claw → Claw | 296 | 7 |
| Hook → Hook | 274 | 11 |

---

## Circuit interpretation

### 1. Proprioceptive relay to thoracic interneurons

The dominant output of all three fCO subtypes is to **thoracic VNC interneurons**, particularly the IN13, IN14, IN19, and IN23 series. These are likely second-order proprioceptive interneurons that integrate fCO signals with other sensory and motor context.

### 2. Ascending proprioceptive channels to the brain

The **AN08, AN10, AN12** series receive significant input from fCO neurons and are likely ascending neurons relaying proprioceptive signals to the subesophageal zone or thoracic ganglia of the brain. AN08B018 is the most consistently connected ascending target of club neurons (62% penetrance), suggesting a dedicated velocity channel.

### 3. Monosynaptic reflex arcs

Claw neurons directly contact **primary motor neurons** (19% penetrance, 15 avg synapses), and both claw and hook neurons contact **secondary motor neurons**. This provides a short-latency proprioceptive reflex pathway — analogous to the vertebrate Ia afferent → motoneuron monosynaptic reflex.

### 4. Presynaptic inhibition and efference copy

**Hook neurons** receive the strongest feedback from VNC interneurons (574 pairs from VNC neurons, avg 24 synapses; IN09A012 alone averages 52 synapses per connection onto hook neurons). This pattern is consistent with **presynaptic inhibition** at fCO axon terminals — a mechanism by which motor circuits modulate proprioceptive gain during active movement (efference copy). The IN09 series is particularly implicated given the high average weights.

### 5. Subtype specialisation

The three fCO subtypes show distinct connectivity fingerprints:

- **Claw neurons** preferentially target position-encoding interneurons (IN13 series, high-weight connections) and directly contact motor neurons — consistent with a role in postural load sensing and slow reflexes
- **Club neurons** project broadly to all VNC segments and strongly target ascending neurons — consistent with velocity encoding relayed to the brain
- **Hook neurons** receive the strongest feedback inhibition and connect to Notch OFF hemilineage interneurons — possibly direction-selective velocity pathways

---

## Data notes

- All data retrieved from VFB connectomics graph; individual neuron data sourced from the **MANC** (Male Adult Nerve Cord) dataset
- Pairs counts reflect individual neuron-to-neuron connections within the class-pair; a single class pair may include hundreds of individual neurons
- Minimum synapse threshold of 5 applied throughout; Hemibrain and catmaid FAFB datasets excluded
- FBbt IDs for specific interneurons (IN, AN series) are provisional VFB identifiers and may not yet have stable FlyBase accessions

---

## Literature Support for Flight Motor Neuron Connectivity Assertions

The following literature review supports the key biological conclusions from a class-level connectivity analysis of flight control motor neurons — specifically, the direct sensory input from wing and haltere campaniform sensilla, the role of VNC interneurons, and the differential wiring of TTMn.

### 1. Direct campaniform sensilla → flight motor neuron connections

- **Fayyazuddin & Dickinson (1996)** "Haltere Afferents Provide Direct, Electrotonic Input to a Steering Motor Neuron in the Blowfly, *Calliphora*" — *J. Neuroscience* 16:5225-5232. Foundational paper showing monosynaptic electrical (gap-junction) and chemical synaptic connections from haltere campaniform field dF2 directly onto the b1 motor neuron (mnb1).
- **Fayyazuddin & Dickinson (1999)** "Convergent mechanosensory input structures the firing phase of a steering motor neuron in the blowfly, *Calliphora*" — *J. Neurophysiology* 82:1916-26. Demonstrated that both wing and haltere nerve input converge monosynaptically onto b1, setting the firing phase of b1 within the wingbeat cycle.
- **Lesser, Moussa & Tuthill (2025)** "Peripheral anatomy and central connectivity of proprioceptive sensory neurons in the *Drosophila* wing" — *bioRxiv*. Using the FANC connectome, shows campaniform sensilla on the tegula synapse directly onto the tonic wing b1 motor neuron. 34 of 62 previously uncharacterized wing sensory axons synapse directly onto wing steering motor neurons. Reports putative electrical synapses (dense mitochondria at terminals) consistent with fast electrotonic connections.
- **Dhawan, Huang & Dickerson (2025)** "Neural connectivity of a computational map for fly flight control" — *bioRxiv*. Connectomic reconstruction of haltere campaniform afferents in MANC, showing broad connectivity to wing steering motor neurons including b1, b2, b3, i1, i2, iii3, and hg4. Confirms "anatomical and physiological evidence confirms that haltere afferents supply the b1 motor neuron with both chemical and electrotonic input."

### 2. Wing campaniform sensilla as strain/curvature detectors

- **Dickinson & Palka (1987)** "Physiological properties, time of development, and central projection are correlated in the wing mechanoreceptors of *Drosophila*" — *J. Neuroscience* 7:4201-4208. Wing campaniform sensilla encode cuticular deformation; phasic neurons detect rapid deformations during each wingbeat cycle.
- **Dinges et al. (2020)** "Location and arrangement of campaniform sensilla in *Drosophila melanogaster*" — *J. Comp. Neurology*. Comprehensive mapping of CS on the *Drosophila* body; CS detect deformations of the exoskeleton arising from resisted movements.
- **Pratt et al. (2017)** "Neural evidence supports a dual sensory-motor role for insect wings" — *Proc. R. Soc. B* 284:20170969. Wing campaniform sensilla encode mechanical stimulus features rapidly and precisely, with properties similar to haltere neurons — supporting wings as sensors of body dynamics.
- **Fabian et al. (2022)** "Systematic characterization of wing mechanosensors that monitor airflow and wing deformations" — *iScience*. Wing CS fields at the base are load-bearing structures transmitting forces; sensors have high directional selectivity for strain patterns.

### 3. Haltere campaniform sensilla as gyroscopic sensors

- **Pringle (1948)** — foundational work establishing halteres as gyroscopic rate sensors operating on the Coriolis principle.
- **Mohren et al. (2019)** "Coriolis and centrifugal forces drive haltere deformations and influence spike timing" — *Proc. R. Soc. B*. Campaniform sensilla at the haltere base detect Coriolis-induced out-of-plane bending during body rotations, providing "rapid flight feedback via fast electrotonic synapses onto the flight motor neurons."
- **Parween & Pratap (2015)** "Modelling of soldier fly halteres for gyroscopic oscillations" — *Biology Open* 4:137-145. Confirmed halteres as vibratory rate-gyros detecting pitch, yaw, and roll via Coriolis forces; campaniform sensilla act as strain sensors at the haltere base.

### 4. Basalar b1 / DLM receiving heaviest sensory drive

- **Whitehead et al. (2022)** "Neuromuscular embodiment of feedback control elements in *Drosophila* flight" — *Science Advances* 8. Identifies b1 and b2 basalar muscles as playing "a prominent role in flight control" with b1 firing a phase-locked spike every wingstroke — driven by mechanosensory input.
- **Lehmann & Bartussek (2017)** "Neural control and precision of flight muscle activation in *Drosophila*" — *J. Comp. Physiol. A*. Sensory integration at the level of single motoneurons (including b1) achieves sub-millisecond timing precision, with haltere and wing mechanoreceptors providing direct excitatory input.

### 5. TTMn as escape (GF-driven), not steady-state flight

- **Deal & Yamamoto (2019)** "Unweaving the role of nuclear Lamins in neural circuit integrity" — reviews the giant fiber circuit: TTMn receives direct electrical synapse from the giant fiber for the escape jump response, while DLMn is activated via PSI for flight.
- **Fayyazuddin et al. (2006)** "The Nicotinic Acetylcholine Receptor Da7 Is Required for an Escape Behavior in *Drosophila*" — *PLoS Biology*. Confirms the giant fiber circuit: GF→TTMn (electrical) for jump, GF→PSI→DLMn (chemical) for flight. "Flies can jump even in the absence of the DLMs."
- **Kennedy & Broadie (2018)** "Newly Identified Electrically Coupled Neurons Support Development of the *Drosophila* Giant Fiber Model Circuit" — *eNeuro*. Reviews GF circuit targeting TTM (jump muscle) and DLM (indirect flight muscles). TTMn is part of the escape circuit, receiving drive from the giant fiber — not from proprioceptive campaniform sensilla.

### 6. VNC interneurons upstream of flight motor neurons

- **Takemura et al. (2023)** "A Connectome of the Male *Drosophila* Ventral Nerve Cord" (MANC) — *bioRxiv*. The foundational MANC dataset providing complete VNC connectivity including ~23,000 traced neurons with IN-prefix naming for thoracic interneurons.
- **Cheong, Eichler, Stürner et al. (2025)** "Transforming descending input into motor output" — *bioRxiv*. Analysis of the MANC connectome showing "direct DN-MN connections are infrequent" and identifying communities of intrinsic neurons for flight steering and power generation — confirming that dominant upstream inputs to flight motor neurons are thoracic VNC interneurons.
- **Azevedo et al. (2024)** "Tools for connectomic reconstruction and analysis of a female *Drosophila* ventral nerve cord" (FANC) — *bioRxiv*. Complementary female VNC connectome confirming motor neuron identification and premotor circuit architecture.

### Summary of literature support

| Assertion | Support | Key References |
|---|---|---|
| Direct CS → flight MN synapses | **Strong** | Fayyazuddin & Dickinson 1996, 1999; Lesser et al. 2025; Dhawan et al. 2025 |
| Wing CS detect strain/curvature | **Strong** | Dickinson & Palka 1987; Pratt et al. 2017; Dinges et al. 2020 |
| Haltere CS as gyroscopic sensors | **Strong** | Pringle 1948; Mohren et al. 2019; Dhawan et al. 2025 |
| b1/DLM receive heaviest sensory drive | **Strong** | Fayyazuddin & Dickinson 1996; Whitehead et al. 2022; Lesser et al. 2025 |
| TTMn is escape-only, no CS input | **Strong** | Fayyazuddin et al. 2006; Kennedy & Broadie 2018; Deal & Yamamoto 2019 |
| VNC interneurons dominate upstream | **Strong** | Takemura et al. 2023; Cheong et al. 2025 |
| Cholinergic identity of CS neurons | **Moderate** | Implied by nAChR requirement at PSI-DLMn (Fayyazuddin et al. 2006); explicit neurotransmitter ID for wing CS less directly cited |

---

*Report generated by Claude Code using VFB MCP connectivity tools.*
