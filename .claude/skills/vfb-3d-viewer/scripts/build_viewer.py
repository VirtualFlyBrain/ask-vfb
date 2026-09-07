#!/usr/bin/env python3
"""Build a self-contained interactive 3D viewer of VFB neuron skeletons.

Given a spec describing a set of VFB image IDs (individual neurons with a
skeleton) and their alignment template, this downloads the SWC skeletons and,
optionally, the template surface mesh from virtualflybrain.org, co-registers
them, and writes a single standalone HTML file that renders them with WebGL
(three.js, loaded from cdnjs). No server or build step is needed to view it.

The heavy lifting of *finding* the right images is done by Claude via the VFB
MCP (get_term_info -> ListAllAvailableImages). This script only takes the
resolved IDs and turns them into a viewer.

Spec JSON (passed with --spec, or piped on stdin):

    {
      "title":    "b2 motor neurons",
      "subtitle": "wing basalar muscle b2 MN · FBbt_00004068",   # optional
      "template": { "id": "VFB_00200000", "label": "JRCVNC2018U",
                    "render_mesh": true },                        # id required
      "neurons": [
        {"id":"VFB_jrmc02fh","label":"b2 MN_L","src":"MaleCNS:801137",
         "ds":"Male CNS v0.9"},
        ...
      ]
    }

`template.id` is always required: it is the alignment space, and each neuron's
SWC is fetched from that template's data path. `template.render_mesh` (default
true) controls whether the template *surface* is also embedded as a translucent
shell. `label`, `src`, `ds` are display-only and may be omitted.

Usage:
    python build_viewer.py --spec spec.json --out viewer.html
    cat spec.json | python build_viewer.py --out viewer.html
"""
import argparse
import base64
import json
import os
import struct
import sys
import urllib.request
import urllib.error

DATA_ROOT = "https://www.virtualflybrain.org/data/VFB/i"

# Distinct, colourblind-aware pairs: bright hue for the dark backdrop, a deeper
# version of the same hue for the light backdrop. Cycled if there are more
# neurons than entries.
PALETTE = [
    {"dark": "#53d4ff", "light": "#0072b0"},  # cyan
    {"dark": "#ff5aa2", "light": "#c0184a"},  # pink
    {"dark": "#ffc247", "light": "#b26a00"},  # amber
    {"dark": "#7ff0a8", "light": "#2c8a54"},  # mint
    {"dark": "#b79cff", "light": "#6a3fd6"},  # violet
    {"dark": "#ff9d5c", "light": "#c05a10"},  # orange
    {"dark": "#cbe86b", "light": "#6b8e00"},  # lime
    {"dark": "#6fb7ff", "light": "#1f5fb0"},  # sky
    {"dark": "#ff8fb0", "light": "#b03a5e"},  # rose
    {"dark": "#5fe0d0", "light": "#128a7a"},  # teal
]

TEMPLATE_HTML = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                             "viewer_template.html")


def id_to_path(vfb_id):
    """VFB_jrmc02fh -> ('jrmc', '02fh'); VFB_00200000 -> ('0020', '0000')."""
    core = vfb_id.strip()
    if core.startswith("VFB_"):
        core = core[4:]
    if len(core) < 8:
        raise ValueError("unexpected VFB id (need 8 chars after VFB_): %r" % vfb_id)
    return core[:4], core[4:8]


def fetch(url, timeout=90):
    req = urllib.request.Request(url, headers={"User-Agent": "ask-vfb/vfb-3d-viewer"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


def fetch_text(url, timeout=90):
    return fetch(url, timeout).decode("utf-8", "replace")


def swc_url(neuron_id, template_id):
    p1, p2 = id_to_path(neuron_id)
    return "%s/%s/%s/%s/volume.swc" % (DATA_ROOT, p1, p2, template_id)


def obj_url(template_id):
    p1, p2 = id_to_path(template_id)
    return "%s/%s/%s/%s/volume_man.obj" % (DATA_ROOT, p1, p2, template_id)


def parse_swc(text):
    """Return list of (x, y, z, parent_index0) with a remap to 0-based indices."""
    raw = {}
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        p = line.split()
        if len(p) < 7:
            continue
        raw[int(p[0])] = (float(p[2]), float(p[3]), float(p[4]), int(p[6]))
    remap = {n: j for j, n in enumerate(raw)}
    return raw, remap


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--spec", help="path to spec JSON (default: read stdin)")
    ap.add_argument("--out", required=True, help="output HTML path")
    ap.add_argument("--no-template-mesh", action="store_true",
                    help="skip embedding the template surface even if requested")
    args = ap.parse_args()

    spec = json.load(open(args.spec)) if args.spec else json.load(sys.stdin)

    neurons_in = spec.get("neurons") or []
    if not neurons_in:
        sys.exit("spec has no 'neurons'")
    template = spec.get("template") or {}
    template_id = template.get("id")
    if not template_id:
        sys.exit("spec.template.id is required (the alignment space for the SWCs)")
    tmpl_label = template.get("label", template_id)
    render_mesh = template.get("render_mesh", True) and not args.no_template_mesh

    # ---- collect skeletons; establish a shared centre + scale ----
    parsed = []
    all_pts = []
    for n in neurons_in:
        url = swc_url(n["id"], template_id)
        try:
            raw, remap = parse_swc(fetch_text(url))
        except urllib.error.HTTPError as e:
            print("  ! %s: no SWC (HTTP %s) - skipped" % (n["id"], e.code), file=sys.stderr)
            continue
        except Exception as e:  # noqa: BLE001
            print("  ! %s: %s - skipped" % (n["id"], e), file=sys.stderr)
            continue
        if not raw:
            print("  ! %s: empty SWC - skipped" % n["id"], file=sys.stderr)
            continue
        parsed.append((n, raw, remap))
        for i, (x, y, z, _p) in raw.items():
            all_pts.append((x, y, z))
        print("  + %s: %d nodes" % (n["id"], len(raw)), file=sys.stderr)

    if not parsed:
        sys.exit("no neuron had a usable SWC skeleton in template %s" % template_id)

    xs = [p[0] for p in all_pts]; ys = [p[1] for p in all_pts]; zs = [p[2] for p in all_pts]
    cx = (min(xs) + max(xs)) / 2.0
    cy = (min(ys) + max(ys)) / 2.0
    cz = (min(zs) + max(zs)) / 2.0
    span = max(max(xs) - min(xs), max(ys) - min(ys), max(zs) - min(zs)) or 1.0
    scale = 100.0 / span

    def tx(x, y, z):
        return (round((x - cx) * scale, 3),
                round((y - cy) * scale, 3),
                round((z - cz) * scale, 3))

    # ---- build neuron records ----
    neurons_out = []
    for k, (n, raw, remap) in enumerate(parsed):
        pos = []
        edges = []
        for node, (x, y, z, _p) in raw.items():
            X, Y, Z = tx(x, y, z)
            pos += [X, Y, Z]
        for node, (x, y, z, par) in raw.items():
            if par != -1 and par in remap:
                edges += [remap[par], remap[node]]
        neurons_out.append({
            "key": n["id"],
            "label": n.get("label", n["id"]),
            "src": n.get("src", ""),
            "ds": n.get("ds", ""),
            "color": PALETTE[k % len(PALETTE)],
            "pos": pos,
            "edges": edges,
        })

    neuron_data = json.dumps({"neurons": neurons_out}, separators=(",", ":"))

    # ---- optional template surface ----
    tmpl_data = ""
    if render_mesh:
        try:
            verts, faces = [], []
            for line in fetch_text(obj_url(template_id)).splitlines():
                if line.startswith("v "):
                    _, a, b, c = line.split()[:4]
                    verts.append(tx(float(a), float(b), float(c)))
                elif line.startswith("f "):
                    idx = [int(t.split("/")[0]) - 1 for t in line.split()[1:]]
                    for m in range(1, len(idx) - 1):        # fan-triangulate
                        faces.append((idx[0], idx[m], idx[m + 1]))
            if verts and faces:
                pos_b = struct.pack("<%df" % (len(verts) * 3),
                                    *[v for t in verts for v in t])
                flat = [i for f in faces for i in f]
                idx_b = struct.pack("<%dI" % len(flat), *flat)
                tmpl_data = json.dumps({
                    "nverts": len(verts), "nfaces": len(faces),
                    "pos": base64.b64encode(pos_b).decode(),
                    "idx": base64.b64encode(idx_b).decode(),
                }, separators=(",", ":"))
                print("  + template %s: %d verts / %d faces"
                      % (template_id, len(verts), len(faces)), file=sys.stderr)
        except Exception as e:  # noqa: BLE001
            print("  ! template mesh unavailable (%s) - viewer built without it" % e,
                  file=sys.stderr)

    # ---- assemble HTML ----
    title = spec.get("title", "VFB neurons")
    subtitle = spec.get("subtitle") or (
        "%d neuron%s · aligned to %s"
        % (len(neurons_out), "" if len(neurons_out) == 1 else "s", tmpl_label))
    credit = spec.get("credit") or ("Skeletons aligned to %s" % tmpl_label)

    html = open(TEMPLATE_HTML).read()
    html = html.replace("/*NEURON_DATA*/", neuron_data)
    html = html.replace("/*TMPL_DATA*/", tmpl_data)
    html = html.replace("/*PAGE_TITLE*/", title)
    html = html.replace("/*TITLE*/", title)
    html = html.replace("/*SUBTITLE*/", subtitle)
    html = html.replace("/*CREDIT*/", credit)

    with open(args.out, "w") as f:
        f.write(html)

    mb = len(html.encode()) / 1e6
    warn = "  (WARNING: exceeds the 16 MB artifact limit)" if mb > 16 else ""
    print("\nWrote %s  (%.2f MB, %d neurons%s)%s"
          % (args.out, mb, len(neurons_out),
             ", + template shell" if tmpl_data else "", warn),
          file=sys.stderr)


if __name__ == "__main__":
    main()
