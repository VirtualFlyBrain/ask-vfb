## Circuit summary diagram (vertical)

Vertical version of the C2 circuit summary diagram from
[`C2_glutamatergic_input_report_v2.md`](C2_glutamatergic_input_report_v2.md) §7 —
glutamatergic inputs on top, C2 in the middle, downstream targets below.

```mermaid
flowchart TB
    %% Upstream glutamatergic inputs
    L1[L1 — lamina monopolar<br/>glutamatergic, ON pathway]:::glu
    L5[L5 — lamina monopolar<br/>glutamatergic]:::glu
    Pm12[Pm12 — proximal medullary amacrine<br/>glutamatergic]:::glu

    %% C2 itself — autoreceptor noted in node
    C2(("C2<br/>GABAergic centrifugal<br/>1 per visual column<br/>↻ GABA-B-R2 autoreceptor [E]")):::gaba

    %% Downstream targets of C2
    L1t[L1 target<br/>Rdl low + Grd/Lcch3/CG8916]:::target
    L2t[L2 target<br/>Rdl low + Grd/Lcch3/CG8916]:::target
    L5t[L5 target<br/>Rdl high, no Grd/CG8916]:::target

    %% Glutamatergic inputs to C2 — labeled with receptor + sign + connectome weight
    L1 -->|"Glu → GluClα Cl⁻ ⊖ (shunt/hyperpol.)<br/>+ GluRIA, ukar (cation ⊕)<br/>86% C2, ~26 syn/pair, 67k total [E]"| C2
    L5 -->|"Glu → GluClα ⊖ + kainate iGluRs ⊕<br/>83% C2, ~5 syn/pair, 47k total [E]"| C2
    Pm12 -->|"Glu, ~6 syn/pair, 14k total [E]"| C2

    %% C2 outputs — sign hypothesis depends on subunit composition
    C2 ==>|"GABA → Rdl ⊖ (Cl⁻)<br/>+ possibly Grd/Lcch3/CG8916 ⊕ (cation) [H]"| L1t
    C2 ==>|"GABA → Rdl ⊖ + Grd/Lcch3/CG8916 ⊕? [H]"| L2t
    C2 ==>|"GABA → Rdl ⊖ (Cl⁻, classical inhibition)<br/>no Grd/CG8916 [E receptors, H sign]"| L5t

    classDef glu fill:#e6f0ff,stroke:#003a8c,color:#000
    classDef gaba fill:#fff1b8,stroke:#874d00,color:#000
    classDef target fill:#f0f0f0,stroke:#555,color:#000
```

### Legend

**Cell colours**
- 🔵 Blue = glutamatergic input neuron
- 🟡 Yellow = GABAergic centrifugal neuron (C2)
- ⚪ Grey = downstream target of C2 (sign of C2 output not yet measured)

**Edge syntax**
`transmitter → receptor sign (effect)` — e.g. `Glu → GluClα Cl⁻ ⊖`.
- ⊖ = inhibitory / hyperpolarising / shunting
- ⊕ = excitatory / depolarising
- Solid thin arrow = afferent (glutamatergic) input to C2
- Solid thick arrow (==>) = GABAergic output of C2
- Dashed loop = autoreceptor / presynaptic feedback

**Evidence tags**
- **[E]** edge: receptor identity is supported by VFB scRNAseq across multiple datasets and the connection by VFB connectomics; in some cases sign of effect is also supported by published physiology (e.g. GluClα is inhibitory in fly olfaction and medulla, Molina-Obando 2019).
- **[H]** edge: the sign / functional effect is a hypothesis built from receptor co-expression patterns, awaiting direct electrophysiology. In particular, whether the C2→L1/L2 GABAergic synapse is purely inhibitory (via Rdl-Cl⁻ channels), depolarising (via Grd/Lcch3-cation channels), or mixed across cells is currently undetermined.

**Source of numbers in edge labels** — VFB `UpstreamClassConnectivity` on C2, aggregated across MaleCNS, FlyWire/FAFB, hemibrain, JRC OpticLobe and BANC connectomes (n=2,667 C2 instances).
