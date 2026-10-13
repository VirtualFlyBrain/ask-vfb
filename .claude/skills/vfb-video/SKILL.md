---
name: vfb-video
description: Make a short narrated-by-captions 3D video of specific Virtual Fly Brain data — chosen neurons, brain regions or templates — as an MP4 with VFB credit, dataset licences and ready-to-paste reference wording. Use when a user asks for a video, animation, fly-through or rotating 3D clip of named neurons or regions.
user-invocable: true
---

# VFB data video

Turns VFB neurons (skeleton SWC) and brain regions (mesh OBJ) the user names into a rotating, captioned 1080p MP4 on a dark background, ending with a **references and data sources** card. Every frame is a pure function of time, so renders are repeatable and stills can be previewed in seconds.

Use the VFB MCP for all facts and IDs. Never draw or label anything that was not returned by VFB.

---

## Setup (once)

```bash
bash .claude/skills/vfb-video/scripts/setup_video.sh
```

Installs Playwright + Chromium into `.venv` (or `python3`), checks for `ffmpeg`, and caches three.js in `~/.cache/vfb-video`. If `ffmpeg` is missing, tell the user to install it (`brew install ffmpeg` / `sudo apt install ffmpeg`) and stop until it is there. Never use system Python if `.venv` exists.

## Step 1 — Agree the brief (ask only what is missing)

- **What to show**: neuron types, specific individual neurons, brain regions, or a mix. Keep it to **1–8 items** — more is unreadable.
- **Space**: all items must be in the **same template** (default adult brain `VFB_00101567`, JRC2018U). Mixing templates puts things in the wrong place.
- **Length**: default 24 s; allow ~2.5 s per item + 3 s title + 7 s references card.
- **Where it will be used** (talk, web, social): affects licence checks in step 5.

## Step 2 — Collect data with the VFB MCP

1. `search_terms` (use `filter_types`, e.g. `["neuron","has_image"]`) to find IDs. For a *type* ("DA1 lPN") pick individuals with `run_query` → `ListAllAvailableImages`; show the user which individuals you chose.
2. `get_term_info` on each chosen individual. From the response take:
   - `Images["<TEMPLATE_ID>"][i]` → `swc` (neuron skeleton) and `obj` (mesh, file is `volume_man.obj`). Use `swc` for neurons; use `obj` for regions and for neurons that have no SWC.
   - `Licenses` → list of `{source, label, source_iri}`.
   - `Publications` (if any) → `{citation, doi}`.
3. For brain regions: `get_term_info` on the **template** → `Domains` gives each painted domain's `obj`. Use `opacity` 0.25–0.4.
4. `get_term_info` on the template itself for its `Licenses` (the JRC2018 templates are CC-BY-NC-SA-4.0).
5. Note whether you used the VFB MCP (`used_mcp: true`) — it adds the MCP citation.

## Step 3 — Write `spec.json`

Work in `videos/<name>/` (the `videos/` folder is git-ignored). Start from `.claude/skills/vfb-video/example/spec.json`.

```json
{
  "title": "...", "subtitle": "...",
  "duration": 24, "fps": 30, "width": 1920, "height": 1080,
  "used_mcp": true, "used_ontology": true,
  "zoom_out": 1.5, "orbit_turns": 0.6,
  "template": {"id": "VFB_00101567", "label": "JRC2018U adult brain",
               "obj": "https://www.virtualflybrain.org/data/VFB/i/0010/1567/VFB_00101567/volume_man.obj",
               "licenses": [{"source": "...", "label": "..."}]},
  "items": [
    {"id": "VFB_00101199", "label": "short caption", "color": "#4c8dff",
     "swc": "https://www.virtualflybrain.org/data/VFB/i/0010/1199/VFB_00101567/volume.swc",
     "licenses": [...], "publications": [{"citation": "...", "doi": "..."}]}
  ]
}
```

Rules: URLs must be the `https://www.virtualflybrain.org/data/...` ones from `Images` (the script refuses others); captions short (≤ 40 characters) — label with the name first, ID last; omit `template.obj` for a clean black background; set `"used_ontology": false` if no FBbt anatomy terms are named.

## Step 4 — Prepare, preview, render

```bash
PY=.venv/bin/python; S=.claude/skills/vfb-video/scripts
$PY $S/prepare.py videos/<name>/spec.json videos/<name>/work      # downloads data, writes references.md
$PY $S/render_video.py videos/<name>/work --stills 2,8,16,22       # JPEG previews in work/stills/ (seconds)
```

Look at the stills (Read the images): neurons visible and sensibly framed, captions not cut off, end card readable. Adjust `zoom_out` (framing), colours or labels and re-run `render_video.py --stills`. Then:

```bash
$PY $S/render_video.py videos/<name>/work videos/<name>/<name>.mp4
```

Rendering is software GL: expect roughly 0.1–0.4 s per frame (a 24 s, 30 fps clip ≈ 2–5 minutes; faster without the template mesh). Progress prints every 5 s. The video has no audio — all messages are on screen.

## Step 5 — Licence check, then hand over

`prepare.py` prints `NOTE:` lines for licences that restrict use. Relay them: the JRC2018 templates are **non-commercial** (CC-BY-NC-SA), so a video showing the template must not be used commercially; if the user needs that, re-run without `template.obj`. Anything that is not CC-BY needs its terms checked before public posting. Do not guess a licence — only use what `get_term_info` returned.

Give the user: the MP4 path, the `references.md` path, the acknowledgement paragraph pasted into the reply, and the list of VFB links (`https://v2.virtualflybrain.org/org.geppetto.frontend/geppetto?id=<VFB_ID>&i=<TEMPLATE_ID>,<IMAGE_ID>`) for each item.

---

## How to reference VFB and the data (use this wording)

**Always cite the primary VFB paper**, in the video description, slide notes, figure legend or methods:

> Court, R., Costa, M., Pilgrim, C., Millburn, G., Holmes, A., McLachlan, A., Larkin, A., Matentzoglu, N., Kir, H., Parkinson, H., Brown, N. H., O'Kane, C. J., Armstrong, J. D., Jefferis, G. S. X. E., & Osumi-Sutherland, D. (2023). Virtual Fly Brain—An interactive atlas of the Drosophila nervous system. *Frontiers in Physiology*, 14. https://doi.org/10.3389/fphys.2023.1076533

- **If the data were found through the VFB MCP / Claude**, also cite: McLachlan, A. D., Court, R., Pilgrim, C., Longden, K., Brown, N. H., Osumi-Sutherland, D., Jefferis, G. S. X. E., & Armstrong, J. D. (2026). *VFB-MCP: Natural-language access to Drosophila neuroscience grounded by an expert-curated ontology-led knowledgebase* [Preprint]. bioRxiv. https://doi.org/10.64898/2026.06.16.732577 (preprint — cite the peer-reviewed version if one has appeared).
- **If anatomy terms (FBbt) are named**, also cite: Osumi-Sutherland, D., Reeve, S., Mungall, C. J., Neuhaus, F., Ruttenberg, A., Jefferis, G. S., & Armstrong, J. D. (2012). A strategy for building neuroanatomy ontologies. *Bioinformatics*, 28(9). https://doi.org/10.1093/bioinformatics/bts113
- **Acknowledge the original data providers** — the dataset names and licences from each item's `Licenses` (e.g. "EM FAFB Zheng et al 2018, CC-BY 4.0") and any `Publications` returned. `prepare.py` collects them into `references.md`.

**Acknowledgement sentence** (generated by `prepare.py` with the real datasets and today's access date):

> Neuron and brain-region data in this video were obtained from Virtual Fly Brain (virtualflybrain.org; Court et al. 2023), accessed <date> through the VFB MCP tool (McLachlan et al. 2026). Underlying datasets: <dataset (licence); …>.

The video's own closing card shows the same sources automatically. Do not remove it from videos that will be shared; if the user wants a different end card, edit `end_card_lines` in `work/spec.resolved.json` and re-render, keeping the VFB paper and dataset lines.

## Gotchas

- `volume.obj` often 404s; the served mesh is `volume_man.obj`. Some individuals have no `swc` — use `obj`.
- Skeleton and mesh coordinates are in template space (µm); that is why all items must share a template.
- Large template meshes slow rendering; for faster drafts drop `template.obj` or lower `fps` to 24.
- The clip is a visualisation, not an analysis: describe only what VFB returned (names, datasets, connectivity numbers from the `vfb-connectivity` skill). Do not claim function or connectivity that was not queried.
- Downloads use a polite `User-Agent`; if virtualflybrain.org returns 403 the request was blocked — report it rather than retrying in a loop.
