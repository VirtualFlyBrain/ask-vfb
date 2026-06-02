# Glutamatergic Input to the *Drosophila* Centrifugal Neuron C2 — v2

Cross-referenced VFB scRNAseq, VFB connectomics, and published literature to characterise the glutamatergic input to [centrifugal neuron C2](https://v2.virtualflybrain.org/org.geppetto.frontend/geppetto?id=FBbt_00003743) and to spell out what this means for visual signal processing.

**Conventions used throughout**
- [**E**] = directly observed in the VFB data we queried, or reported as a primary observation in cited literature
- [**H**] = inference / model / hypothesis built from those observations (sometimes contested or untested)
- A claim with no marker is descriptive/anatomical background derivable from the ontology or canonical figures

---

## 1. Identity and wiring of C2

[**E**] *VFB term info on [FBbt_00003743](https://v2.virtualflybrain.org/org.geppetto.frontend/geppetto?id=FBbt_00003743) and the underlying primary literature.*

- Per-column small-field columnar centrifugal neuron in the optic lobe (~1 per visual column, ≈750 columns).
- Receives input in the proximal medulla; sends GABAergic output back to the lamina, with terminals on L1 and L2 "necks" and synapses on L5 and Mi1 in the medulla (Fischbach & Dittrich 1989; Takemura et al. 2013; Nern et al. 2025).
- Annotated **GABAergic** in VFB; GABA + GAD + vGAT confirmed by antibody (Kołodziejczyk et al. 2008).

---

## 2. Glutamatergic receptor repertoire of C2 (5 scRNAseq datasets) [E]

Values are `expression level / extent` (extent = fraction of C2 cells in which the gene is detected). Pulled by `clusterExpression` on the per-dataset C2 clusters.

| Receptor | Type | Ozel 21 (OL) | Kurmang 20 (OL) | FCA-F head | FCA-M head | Davie 18 | Robustness |
|---|---|---|---|---|---|---|---|
| [GluClα](https://v2.virtualflybrain.org/org.geppetto.frontend/geppetto?id=FBgn0024963) | Cl⁻ channel (inhibitory) | 844 / 0.22 | 601 / 0.89 | 1474 / 0.46 | 1614 / 0.56 | 919 / 0.38 | **5/5** |
| [GluRIA](https://v2.virtualflybrain.org/org.geppetto.frontend/geppetto?id=FBgn0004619) | kainate-clade iGluR | – | 783 / 0.90 | 1481 / 0.50 | 1864 / 0.33 | 874 / 0.42 | 4/5 |
| [ukar](https://v2.virtualflybrain.org/org.geppetto.frontend/geppetto?id=FBgn0039927) | kainate-clade iGluR | – | 380 / 0.80 | 1522 / 0.54 | 1440 / 0.67 | 775 / 0.41 | 4/5 |
| [KaiR1D](https://v2.virtualflybrain.org/org.geppetto.frontend/geppetto?id=FBgn0038837) | kainate-clade iGluR | – | 200 / 0.27 | – | – | – | 1/5 |
| mGluR | metabotropic | – | – | – | – | – | **0/5** |
| Nmdar1 / Nmdar2 | NMDA | – | – | – | – | – | **0/5** |

[**E**] C2 expresses an inhibitory glutamate-gated Cl⁻ channel **plus** kainate-type ionotropic GluRs, in every dataset checked.
[**E**] mGluR and NMDA receptors are not detected in any of the 5 datasets.

[**H**] Functional inference: glutamate would drive a fast cation-permeable EPSP (via kainate iGluRs) with a slower / sustained Cl⁻ shunt or hyperpolarisation (via GluClα). No NMDA-style coincidence detection; no slow metabotropic glutamate modulation. *(This is a model based on canonical receptor biophysics, not direct recording of C2's glutamate response in Drosophila.)*

---

## 3. Connectomic confirmation of glutamatergic input [E]

`UpstreamClassConnectivity` on [FBbt_00003743](https://v2.virtualflybrain.org/org.geppetto.frontend/geppetto?id=FBbt_00003743) aggregated across all VFB-loaded connectomes (MaleCNS, FlyWire/FAFB, hemibrain, JRC OpticLobe, BANC; 2,667 C2 instances total).

| Upstream class | % C2 cells contacted | Total syn | Pairs | Avg syn/pair |
|---|---:|---:|---:|---:|
| [glutamatergic neuron](https://v2.virtualflybrain.org/org.geppetto.frontend/geppetto?id=FBbt_00100291) (aggregate) | 88 % | **77 095** | 4 421 | **17.4** |
| [L1](https://v2.virtualflybrain.org/org.geppetto.frontend/geppetto?id=FBbt_00003719) | 86 % | 67 381 | 2 610 | 25.8 |
| [L5](https://v2.virtualflybrain.org/org.geppetto.frontend/geppetto?id=FBbt_00003725) | 83 % | 46 607 | 9 853 | 4.7 |
| [Pm12](https://v2.virtualflybrain.org/org.geppetto.frontend/geppetto?id=FBbt_20011494) | 71 % | 14 050 | 2 203 | 6.4 |
| [proximal medullary amacrine](https://v2.virtualflybrain.org/org.geppetto.frontend/geppetto?id=FBbt_00003832) (umbrella) | 74 % | 15 532 | 2 777 | 5.6 |
| [Tm4](https://v2.virtualflybrain.org/org.geppetto.frontend/geppetto?id=FBbt_00003788) | 30 % | 3 148 | 1 029 | 3.1 |
| [Mi9](https://v2.virtualflybrain.org/org.geppetto.frontend/geppetto?id=FBbt_00111052) | 3 % | 263 | 88 | 3.0 |
| [Dm9](https://v2.virtualflybrain.org/org.geppetto.frontend/geppetto?id=FBbt_00003841) | 1 % | 51 | 22 | 2.3 |

[**E**] L1 supplies ~87 % of the total "glutamatergic neuron" synaptic weight onto C2 and averages ~26 syn per L1→C2 pair; the result is reproducible across all VFB connectomes.

[**H**] Combining the connectomic numbers with C2's receptor repertoire (§2), L1 is *predicted* to be the principal driver of C2's glutamate response, gating both the GluClα-mediated shunting and the kainate-iGluR-mediated phasic depolarisation. *(Functional recording of L1→C2 transmission has not, to our knowledge, been published in Drosophila; the assignment of effect is biophysical inference.)*

---

## 4. Polarisation logic: what the literature supports

### Direct evidence

[**E**] In adult fly CNS, **glutamate is frequently inhibitory via GluClα**: Liu & Wilson (2013) for olfaction; Molina-Obando et al. (2019) for ON-selectivity in the *medulla* (Mi9 → Mi1/Tm3 via GluClα); Fan et al. (2025) for sleep-promoting VNC neurons. C2 expresses GluClα robustly (5/5).

[**E**] In situ, intracellular recordings of C2 (Douglass & Strausfeld 1995, in a larger fly with conserved wiring) showed a strong **ON-flicker depolarisation** and **sustained motion-evoked hyperpolarisation**.

[**E**] Drosophila CNS iGluRs are exclusively kainate-clade (Han et al. 2024), so cation-permeable when activated. C2 expresses GluRIA + ukar.

### Inference

[**H**] The Douglass–Strausfeld kinetics (phasic ON depolarisation, sustained hyperpolarisation during motion) are *consistent with* — but not formally proven to be caused by — fast kainate-iGluR drive plus slow GluClα shunting from L1. The recording does not separate the two receptor contributions, and the species is not Drosophila.

[**H**] Predicted net effect of L1 → C2 glutamate transmission in Drosophila C2: brief depolarising EPSP followed by/superimposed on a longer-lasting shunting/hyperpolarising Cl⁻ conductance that reduces the gain of concurrent excitatory input (notably nAChRα7 and ort).

---

## 5. Behavioural / circuit evidence for C2's role in vision

| Observation | Reference | Marker |
|---|---|---|
| Silencing C2/C3 changes the fly's response to asymmetric motion stimuli. Authors propose presynaptic inhibition by C2/C3 at L1/L2/L3 medulla terminals implements asymmetric ON/OFF filtering. | Tuthill et al. 2013 | **E** (behavioural + genetic loss-of-function) |
| Activating or silencing C2 (and C3) shifts climbing decisions in a parallax-motion gap-crossing assay ("overeager" vs "overcautious"); C2 manipulation alters the *perceived strength* of parallax motion. | Triphan et al. 2016 | **E** (behavioural + genetic) |
| GABA + GAD + vGAT confirmed in C2; GABA-B-R2 immunoreactivity localised to C2's own terminals (presynaptic GABA-B autoregulation). | Kołodziejczyk et al. 2008 | **E** (immunohistochemistry) |
| L1 and L2 are vGluT⁺ / Glu⁺ (i.e. the connectomic L1 → C2 connection is a *functionally* glutamatergic synapse). | Kołodziejczyk et al. 2008; Raghu & Borst 2011 | **E** (immunohistochemistry) |
| C2 / C3 = per-column negative feedback motif from medulla to lamina. | Fischbach & Dittrich 1989; Takemura et al. 2013 | Anatomical |
| L1 → C2 as the dominant glutamatergic input *predicted to drive* GluClα-mediated shunting in C2. | This report | **H** |
| Glutamate input acts as a local **contrast / luminance gain-control signal** to C2 that the loop returns onto L1/L2/L5/Mi1. | Tuthill 2013; Triphan 2016 — interpretive | **H** (interpretive synthesis, consistent with behaviour but not directly recorded) |

---

## 6. The return limb: is C2 → L1/L2 GABA inhibitory, excitatory, or mixed?

Davis et al. (2020) proposed that L1 and L2 might respond to GABA via **cation-permeable GABA channels** because they lack Rdl but express the Grd / Lcch3 / CG8916 subunit set (which in vitro can form depolarising GABA channels — Gisselmann et al. 2004). They cited Hardie's (1987) classical recordings of *Musca* lamina monopolars depolarising to GABA in support.

Our cross-dataset transcriptomics partly supports this but tempers the strong form of the claim:

### GABA-A subunit expression — C2 vs L1 vs L2 [E]

(format: `level / extent`)

| Subunit | C2 (5 ds) | L1 (5 ds) | L2 (5 ds) |
|---|---|---|---|
| [Rdl](https://v2.virtualflybrain.org/org.geppetto.frontend/geppetto?id=FBgn0004244) (Cl⁻) | **5/5, extent 0.83–0.96** (1713–6073) | 5/5 but **low extent 0.27–0.59** (352–2841) | 4/5, low extent 0.27–0.48 (313–2545) |
| [Grd](https://v2.virtualflybrain.org/org.geppetto.frontend/geppetto?id=FBgn0001134) (cation candidate) | **0/5 — absent** | 4/5, extent 0.23–0.46 (335–1278) | **5/5, extent 0.28–0.66** (342–1314) |
| [Lcch3](https://v2.virtualflybrain.org/org.geppetto.frontend/geppetto?id=FBgn0010240) (β-subunit) | 4/5, extent 0.33–0.64 (316–1396) | 4/5, extent up to 0.80 (308–1308) | 3/5, extent up to 0.80 (312–484) |
| [CG8916](https://v2.virtualflybrain.org/org.geppetto.frontend/geppetto?id=FBgn0030707) (cation candidate) | **0/5 — absent** | 3/5, extent up to 0.54 (295–739) | 3/5, extent up to 0.70 (327–674) |

### Interpretation

[**E**] Rdl **is** detected in L1 and L2 in our data — Davis et al.'s strong "L1/L2 lack Rdl" formulation is not strictly accurate against the VFB scRNAseq. What is supported is the relative claim: Rdl extent in L1/L2 is much lower than in C2 (∼0.3 vs ∼0.9).

[**E**] L1 and L2 do co-express the **Grd + Lcch3 + CG8916** subunit set Davis et al. invoked for cation-permeable GABA channels.

[**E**] C2 itself expresses **only Rdl + Lcch3** of the four subunits — Grd and CG8916 are entirely absent across all 5 datasets.

[**H**] **Sign-asymmetric loop hypothesis (refined):** the L1 ↔ C2 loop has the *potential* to be sign-asymmetric. The L1 → C2 limb is biophysically expected to be inhibitory/shunting (GluClα). The C2 → L1/L2 return limb could be **mixed**: classical Cl⁻ inhibition through Rdl-containing receptors in some L1/L2 cells, and depolarisation through Grd/Lcch3-containing channels in others. This molecular heterogeneity is *consistent with* — but does not on its own demonstrate — the asymmetric-filtering function proposed by Tuthill et al. (2013). Direct electrophysiology of the C2 → L1/L2 synapse in Drosophila would be needed to settle whether Grd/Lcch3 channels operate as cation channels in vivo and how the two GABA-A populations are partitioned across L cells.

---

## 7. Synthesis

[**E**] C2 is a per-column GABAergic centrifugal neuron whose dominant ionotropic input is a glutamatergic projection from L1 (~26 syn / pair, contacting 86 % of C2 cells across all VFB connectomes). C2's receptor repertoire combines a robust glutamate-gated Cl⁻ channel (GluClα) with kainate-type iGluRs (GluRIA, ukar), and lacks both NMDARs and mGluRs.

[**E**] Behavioural manipulation (Tuthill 2013, Triphan 2016) shows C2/C3 are necessary for normal motion-vision responses and for parallax-based distance estimation.

[**H**] The most economical model that ties the receptor expression, connectomics, behavioural genetics, and historical physiology together is that **C2 implements a per-column gain-control module on the early ON pathway**, where L1 glutamate drives GluClα-mediated shunting / hyperpolarisation in C2, kainate-type iGluRs add a fast phasic depolarising component, and C2 returns GABAergic output to L1/L2/L5/Mi1 — potentially sign-asymmetrically given the differential expression of Rdl vs Grd/Lcch3/CG8916 in C2 vs L1/L2. The model is broadly consistent with — and motivated by — Tuthill et al.'s "asymmetric filtering" account, but the precise sign, time-course and gain of each limb has *not* been recorded in Drosophila and is not yet directly supported by physiology.

### What would directly upgrade [H] to [E]
- Patch-clamp or two-electrode recordings of Drosophila C2 with controlled L1 activation (e.g. optogenetic) to confirm the predicted GluClα + kainate-iGluR mix and its kinetics.
- Heterologous reconstitution of fly Grd / Lcch3 / CG8916 combinations to determine in vivo-relevant ion selectivity (Gisselmann et al. 2004 only tested heterologous combinations).
- Cell-type-resolved RNAi or null mutants of GluClα in C2 paired with motion-vision behavioural readouts.

---

## References

- Davie K, Janssens J, Koldere D, et al. *A single-cell transcriptome atlas of the aging Drosophila brain.* Cell 174:982–998 (2018). doi:10.1016/j.cell.2018.05.057
- Davis FP, Nern A, Picard S, Reiser MB, Rubin GM, Eddy SR, Henry GL. *A genetic, genomic, and computational resource for exploring neural circuit function.* eLife (2020). https://pmc.ncbi.nlm.nih.gov/articles/PMC7034979/
- Dorkenwald S, Matsliah A, Sterling AR, et al. *Neuronal wiring diagram of an adult brain (FlyWire).* Nature (2024). https://pmc.ncbi.nlm.nih.gov/articles/PMC11446842/
- Douglass JK & Strausfeld NJ. *Visual motion detection circuits in flies: peripheral motion computation by identified small-field retinotopic neurons.* J Neurosci 15:5596–5611 (1995).
- Fan Y, Tian Y, Han J. *The glutamate-gated chloride channel facilitates sleep by enhancing the excitability of two pairs of neurons in the ventral nerve cord of Drosophila.* (2025). https://pmc.ncbi.nlm.nih.gov/articles/PMC12494514/
- Fischbach K-F & Dittrich APM. *The optic lobe of Drosophila melanogaster. I. A Golgi analysis of wild-type structure.* Cell Tissue Res 258:441–475 (1989).
- Gisselmann G, Plonka J, Pusch H, Hatt H. *Drosophila GRD and LCCH3 subunits form heteromultimeric GABA-gated cation channels.* Br J Pharmacol 142:409–413 (2004).
- Han TH et al. *Neto proteins differentially modulate the gating properties of Drosophila NMJ glutamate receptors.* eLife (2024). https://pmc.ncbi.nlm.nih.gov/articles/PMC11188076/
- Hardie RC. *Is histamine a neurotransmitter in insect photoreceptors?* J Comp Physiol A (1987).
- Kołodziejczyk A, Sun X, Meinertzhagen IA, Nässel DR. *Glutamate, GABA and acetylcholine signaling components in the lamina of the Drosophila visual system.* PLoS ONE 3:e2110 (2008). https://pmc.ncbi.nlm.nih.gov/articles/PMC2373871/
- Kurmangaliyev YZ, Yoo J, Valdes-Aleman J, Sanfilippo P, Zipursky SL. *Transcriptional programs of circuit assembly in the Drosophila visual system.* Neuron 108:1045–1057 (2020).
- Li H et al. (Fly Cell Atlas). Science 375:eabk2432 (2022).
- Liu WW & Wilson RI. *Glutamate is an inhibitory neurotransmitter in the Drosophila olfactory system.* PNAS 110:10294–10299 (2013).
- Lu T-C et al. (Aging FCA). Science 380:eadg0934 (2023).
- Molina-Obando S, Vargas-Fique JF, Henning M, et al. *ON selectivity in the Drosophila visual system is a multisynaptic process involving both glutamatergic and GABAergic inhibition.* eLife 8:e49373 (2019). https://elifesciences.org/articles/49373
- Nern A et al. *Connectome-driven neural inventory of a complete visual system.* (2025) — VFB MaleCNS C2 annotation.
- Özel MN et al. *Neuronal diversity and convergence in a visual system developmental atlas.* Nature 589:88–95 (2021).
- Raghu SV & Borst A. *Candidate glutamatergic neurons in the visual system of Drosophila.* PLoS ONE 6:e19472 (2011).
- Takemura S, Bharioke A, Lu Z, et al. *A visual motion detection circuit suggested by Drosophila connectomics.* Nature 500:175–181 (2013).
- Triphan T, Nern A, Roberts SF, Korff W, Naiman DQ, Strauss R. *A screen for constituents of motor control and decision making in Drosophila reveals visual distance-estimation neurons.* Sci Rep 6:27000 (2016).
- Tuthill JC, Nern A, Holtz SL, Rubin GM, Reiser MB. *Contributions of the 12 neuron classes in the fly lamina to motion vision.* Neuron 79:128–140 (2013).
