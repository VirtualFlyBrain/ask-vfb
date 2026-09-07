---
name: vfb-3d-viewer
description: Build a self-contained, interactive 3D viewer (a single standalone HTML file) of one or more Drosophila neurons from Virtual Fly Brain, rendered as skeletons with an optional translucent alignment-template shell. Use when a user wants to visualise, present, or share neuron morphology in 3D. Works from VFB image IDs of individual neurons that have skeletons (SWC) — typically connectome reconstructions. DO NOT USE for light-level expression patterns (GAL4/split images have no skeleton) or to render dense whole-region populations.
user-invocable: true
---

# VFB 3D Neuron Viewer Builder

Turn a set of VFB neuron images into a single, standalone HTML page that renders
their skeletons in 3D with WebGL (three.js from cdnjs). The page needs no server
and no build step: orbit/zoom/pan, per-neuron show/hide, auto-rotate, reset view,
an optional translucent template shell for anatomical context, and a dark/light
backdrop toggle for slides.

**Why skeletons and not surfaces:** VFB serves each neuron as an SWC skeleton
(~0.5 MB) *and* an OBJ surface mesh. The connectome surface meshes are ~100 MB
each — far too large to embed in a shareable page — so this skill uses the SWC
skeletons. The alignment template's surface *is* embedded (it is a single modest
mesh) as an optional shell.

---

## Setup

Python is run via the repo `.venv` (this script uses only the standard library —
no extra packages — but keep to the house convention). Verify it exists:

```bash
ls .venv/bin/python
```

If missing, run `bash setup_venv.sh` first. Scripts live in
`.claude/skills/vfb-3d-viewer/scripts/` and the HTML template
`viewer_template.html` sits beside `build_viewer.py` — keep them together.

**Never use system Python** (per repo convention).

---

## Instructions

### Step 1: Identify the neurons and their alignment template (VFB MCP)

The build script only turns *resolved IDs* into a viewer — you do the finding.

1. **Resolve the term.** Use `mcp__virtual-fly-brain__search_terms` with
   `filter_types` such as `["neuron"]` (add `"has_image"` to require images).
   Confirm the canonical class (`FBbt_...`) or individual (`VFB_...`) with the
   user if the match is a SYNONYM/BROAD or ambiguous.
2. **Discover the image query.** Call `mcp__virtual-fly-brain__get_term_info` on
   the ID and read its `Queries` array. For a **class**, use
   `ListAllAvailableImages`; for an **individual**, that neuron's own `Images`
   block already lists it.
3. **List the images.** Run `mcp__virtual-fly-brain__run_query` with
   `query_type="ListAllAvailableImages"`. Each row gives:
   - `id` — the VFB image ID (e.g. `VFB_jrmc02fh`) → goes in the spec
   - `label` — display name (e.g. `b2 MN_L`)
   - `source_id` / accession (e.g. `MaleCNS:801137`) → `src`
   - `dataset` (e.g. `Male CNS v0.9`) → `ds`
   - `template` — the alignment space (e.g. `JRCVNC2018U` = `VFB_00200000`)
   Note the `count` and `count_status`. Rows can repeat (one per matched
   synonym) — **de-duplicate by `id`**.
4. **Pick the alignment template.** All neurons in one viewer must share one
   template (their SWCs are stored per template). If images span several
   templates, group by template and confirm which set to render. The template's
   VFB ID is the `VFB_...` in the image link/`template` column
   (e.g. `JRCVNC2018U` → `VFB_00200000`).

**Exclude images with no skeleton**: split-GAL4 / expression-pattern images
(`VFBexp_...`, GAL4 line images) are volumetric light-level data with no SWC.
The script skips anything without an SWC and warns, but don't include them.

### Step 2: Confirm the set with the user

Show the neurons you'll render, the shared template, and whether to include the
template shell. For example:

> I'll build a 3D viewer with these 4 skeletons, aligned to **JRCVNC2018U**:
> - b2 MN_L (MaleCNS:801137), b2 MN_R (MaleCNS:801350)
> - b2 MN (MANC:10131), b2 MN (MANC:10064)
> - **Template shell:** on (translucent VNC outline)
>
> Proceed?

**STOP and wait** unless the user's request already pins all of this down.

### Step 3: Write the spec and build

Write a spec JSON (see the schema in `build_viewer.py`'s header) — one entry per
neuron, plus `template.id` (required — the alignment space) and
`template.render_mesh` (default `true`):

```json
{
  "title": "b2 motor neurons",
  "subtitle": "wing basalar muscle b2 MN &middot; FBbt_00004068 &middot; JRCVNC2018U",
  "template": { "id": "VFB_00200000", "label": "JRCVNC2018U", "render_mesh": true },
  "neurons": [
    {"id":"VFB_jrmc02fh","label":"b2 MN_L","src":"MaleCNS:801137","ds":"Male CNS v0.9"},
    {"id":"VFB_jrmc02fg","label":"b2 MN_R","src":"MaleCNS:801350","ds":"Male CNS v0.9"},
    {"id":"VFB_jrcv07tf","label":"b2 MN","src":"MANC:10131","ds":"MANC v1.0"},
    {"id":"VFB_jrcv07rk","label":"b2 MN","src":"MANC:10064","ds":"MANC v1.2.1"}
  ]
}
```

Then run:

```bash
.venv/bin/python .claude/skills/vfb-3d-viewer/scripts/build_viewer.py \
    --spec spec.json --out outputs/b2_viewer.html
```

| Argument | Required | Description |
|---|---|---|
| `--spec` | No (else stdin) | Path to the spec JSON; omit to pipe on stdin |
| `--out` | Yes | Output HTML path |
| `--no-template-mesh` | No | Skip embedding the template surface even if the spec asks for it |

The script downloads each neuron's SWC and (if requested) the template OBJ from
`virtualflybrain.org`, co-registers them (shared centre + scale from the neuron
points), assigns a distinct colour per neuron, and injects everything into
`viewer_template.html`. It prints a per-neuron node count and the final file
size to stderr.

### Step 4: Deliver

- **If the Artifact tool is available** (Claude Code), publish the HTML as an
  Artifact and give the user the link — it renders the interactive page directly.
- **Otherwise**, save under `outputs/` and tell the user the path; they open the
  `.html` file in any browser (double-click — no server needed).

Report what was built: number of skeletons, the template, and the file size.
Mention any neurons the script skipped (no SWC) and why.

### Step 5: Closing offer

- **Add/remove neurons**: re-run with an edited spec.
- **Anatomical context**: toggle the template shell, or (if off) rebuild with
  `render_mesh: true`.
- **Compare subsets**: the per-neuron toggles in the panel isolate any subset
  (e.g. left vs right, or one dataset).
- **View in VFB**: link the class/individuals to
  `https://v2.virtualflybrain.org/org.geppetto.frontend/geppetto?id=<ID>&i=<TEMPLATE_ID>,<IMG_IDs>`.

---

## Error paths

| Situation | Behaviour |
|-----------|-----------|
| `.venv` not found | Tell the user to run `bash setup_venv.sh` |
| No SWC for an image (HTTP 404) | Script skips it with a warning; if *all* are skipped it exits non-zero — the images are probably expression patterns or lack skeletons |
| Images span multiple templates | Group by template; confirm which set to render (one template per viewer) |
| Template OBJ unavailable | Script builds the viewer without the shell and warns |
| Output > 16 MB | Script warns; too many/too large skeletons — reduce the neuron set or drop the template mesh (`--no-template-mesh`) before publishing as an Artifact |
| Nothing renders in the browser | Confirm WebGL is enabled; the page needs network only to load three.js from cdnjs |

---

## Notes

- **IDs → data path:** a VFB image ID maps to its data folder by splitting the 8
  characters after `VFB_` into two groups of four
  (`VFB_jrmc02fh` → `.../jrmc/02fh/<template_id>/volume.swc`;
  `VFB_00200000` → `.../0020/0000/`). The SWC path always includes the
  **template** ID, because it is the neuron *aligned to that template*.
- **Colours** travel with each neuron in the embedded JSON (a bright hue for the
  dark backdrop, a deeper one for light), cycled from a 10-entry colourblind-aware
  palette in `build_viewer.py`.
- **Coordinates:** SWC and the template OBJ are in the same micron space; the
  script centres on the neuron bounding box and scales the largest dimension to
  ~100 units so the camera framing is stable regardless of the input.
- The viewer is a single file with three.js pulled from cdnjs at runtime — the
  only network dependency once built. Everything else (skeletons, template,
  controls) is embedded.

---

## Testing

```bash
.venv/bin/python -m pytest .claude/skills/vfb-3d-viewer/tests/ -v \
    --rootdir=.claude/skills/vfb-3d-viewer
```

Offline unit tests cover ID→path mapping, SWC parsing and template injection.
One live integration test builds the b2 motor-neuron viewer against VFB and is
skipped automatically when offline. **After any change to the script or
template, ask the user whether to run the suite before considering it done.**
