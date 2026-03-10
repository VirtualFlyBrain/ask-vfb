#!/usr/bin/env python3
"""Generate an interactive HTML circuit diagram from VFB connectivity data."""

import json
import math
import sys
import webbrowser
from pathlib import Path


def load_data(path: str) -> dict:
    with open(path) as f:
        return json.load(f)


def assign_positions(neurons: list) -> dict:
    """Assign x,y positions to neurons based on type, arranged in layers."""
    type_order = {
        "sensory": 0,
        "interneuron": 1,
        "modulatory": 1.5,
        "motor": 2,
        "output": 2,
    }
    layers = {}
    for n in neurons:
        layer = type_order.get(n.get("type", "interneuron"), 1)
        layers.setdefault(layer, []).append(n["id"])

    positions = {}
    sorted_layers = sorted(layers.keys())
    num_layers = len(sorted_layers)
    for li, layer_key in enumerate(sorted_layers):
        ids = layers[layer_key]
        x = 150 + (li / max(num_layers - 1, 1)) * 700
        for ni, nid in enumerate(ids):
            y = 120 + (ni / max(len(ids) - 1, 1)) * 500 if len(ids) > 1 else 370
            positions[nid] = (x, y)
    return positions


NT_COLORS = {
    "acetylcholine": "#4CAF50",
    "gaba": "#E53935",
    "glutamate": "#FB8C00",
    "serotonin": "#AB47BC",
    "dopamine": "#42A5F5",
    "octopamine": "#26A69A",
    "tyramine": "#78909C",
    "histamine": "#8D6E63",
}

SIGN_COLORS = {
    "excitatory": "#4CAF50",
    "inhibitory": "#E53935",
    "modulatory": "#AB47BC",
}

TYPE_SHAPES = {
    "sensory": "triangle",
    "interneuron": "circle",
    "motor": "square",
    "modulatory": "diamond",
    "output": "square",
}


def nt_color(nt: str) -> str:
    if not nt:
        return "#9E9E9E"
    return NT_COLORS.get(nt.lower(), "#9E9E9E")


def sign_color(sign: str) -> str:
    if not sign:
        return "#9E9E9E"
    return SIGN_COLORS.get(sign.lower(), "#9E9E9E")


def generate_html(data: dict, output: Path) -> None:
    neurons = data.get("neurons", [])
    connections = data.get("connections", [])
    hypotheses = data.get("hypotheses", [])
    citations = data.get("citations", [])
    title = data.get("title", "Circuit Diagram")

    positions = assign_positions(neurons)
    neuron_map = {n["id"]: n for n in neurons}

    # Build neuron SVG elements
    neuron_svgs = []
    for n in neurons:
        nid = n["id"]
        x, y = positions.get(nid, (400, 300))
        nt = n.get("neurotransmitter", "")
        color = nt_color(nt)
        ntype = n.get("type", "interneuron")
        name = n.get("name", nid)
        receptors = ", ".join(n.get("receptors", [])) or "unknown"
        nt_ev = n.get("nt_evidence", "")
        func = n.get("known_function", "") or ""

        tooltip = (
            f"{name}\\n"
            f"Type: {ntype}\\n"
            f"NT: {nt or 'unknown'} ({nt_ev})\\n"
            f"Receptors: {receptors}\\n"
            f"Function: {func}"
        )

        shape = TYPE_SHAPES.get(ntype, "circle")
        if shape == "circle":
            el = f'<circle cx="{x}" cy="{y}" r="28" fill="{color}" fill-opacity="0.2" stroke="{color}" stroke-width="2.5" class="neuron" data-id="{nid}"/>'
        elif shape == "triangle":
            pts = f"{x},{y-30} {x-26},{y+18} {x+26},{y+18}"
            el = f'<polygon points="{pts}" fill="{color}" fill-opacity="0.2" stroke="{color}" stroke-width="2.5" class="neuron" data-id="{nid}"/>'
        elif shape == "square":
            el = f'<rect x="{x-24}" y="{y-24}" width="48" height="48" rx="6" fill="{color}" fill-opacity="0.2" stroke="{color}" stroke-width="2.5" class="neuron" data-id="{nid}"/>'
        elif shape == "diamond":
            pts = f"{x},{y-30} {x+26},{y} {x},{y+30} {x-26},{y}"
            el = f'<polygon points="{pts}" fill="{color}" fill-opacity="0.2" stroke="{color}" stroke-width="2.5" class="neuron" data-id="{nid}"/>'
        else:
            el = f'<circle cx="{x}" cy="{y}" r="28" fill="{color}" fill-opacity="0.2" stroke="{color}" stroke-width="2.5" class="neuron" data-id="{nid}"/>'

        label = f'<text x="{x}" y="{y+45}" text-anchor="middle" class="neuron-label">{name}</text>'
        neuron_svgs.append(f'<g data-tooltip="{tooltip}">{el}{label}</g>')

    # Build connection SVG elements
    conn_svgs = []
    # Track edge counts between pairs for curve offsets
    edge_counts = {}
    for c in connections:
        key = tuple(sorted([c["source"], c["target"]]))
        edge_counts[key] = edge_counts.get(key, 0) + 1

    edge_index = {}
    for c in connections:
        src = c["source"]
        tgt = c["target"]
        if src not in positions or tgt not in positions:
            continue
        x1, y1 = positions[src]
        x2, y2 = positions[tgt]
        sc = sign_color(c.get("sign", ""))
        syn = c.get("synapse_count", "?")
        nt = c.get("neurotransmitter", "")
        sign = c.get("sign", "")

        key = tuple(sorted([src, tgt]))
        idx = edge_index.get(key, 0)
        edge_index[key] = idx + 1
        total = edge_counts.get(key, 1)

        # Curve offset for parallel edges
        offset = (idx - (total - 1) / 2) * 40

        mx = (x1 + x2) / 2
        my = (y1 + y2) / 2
        dx = x2 - x1
        dy = y2 - y1
        length = math.sqrt(dx * dx + dy * dy) or 1
        nx = -dy / length
        ny = dx / length
        cx = mx + nx * offset
        cy = my + ny * offset

        marker = "url(#arrow-exc)" if sign != "inhibitory" else "url(#arrow-inh)"
        label_text = f"{nt} ({syn} syn)" if nt else f"{syn} syn"
        tooltip = f"{neuron_map.get(src, {}).get('name', src)} → {neuron_map.get(tgt, {}).get('name', tgt)}\\nSynapses: {syn}\\nNT: {nt}\\nSign: {sign}"

        path = f'<path d="M{x1},{y1} Q{cx},{cy} {x2},{y2}" fill="none" stroke="{sc}" stroke-width="2" stroke-opacity="0.7" marker-end="{marker}" class="connection" data-tooltip="{tooltip}"/>'
        lx = (x1 + 2 * cx + x2) / 4
        ly = (y1 + 2 * cy + y2) / 4
        label = f'<text x="{lx}" y="{ly - 6}" text-anchor="middle" class="conn-label">{label_text}</text>'
        conn_svgs.append(f'{path}{label}')

    # Hypotheses panel
    hyp_html = ""
    for i, h in enumerate(hypotheses):
        conf = h.get("confidence", "unknown")
        conf_color = {"high": "#4CAF50", "medium": "#FB8C00", "low": "#E53935"}.get(conf, "#9E9E9E")
        evidence = ", ".join(h.get("supporting_evidence", []))
        hyp_html += f'''
        <div class="hypothesis">
            <span class="conf-badge" style="background:{conf_color}">{conf}</span>
            <p>{h.get("description", "")}</p>
            <small class="evidence">Evidence: {evidence}</small>
        </div>'''

    # Citations panel
    cit_html = ""
    for c in citations:
        cit_html += f'<li><strong>{c.get("key", "")}</strong>: {c.get("text", "")}</li>'

    # Legend
    legend_nt = "".join(
        f'<span class="legend-item"><span class="legend-dot" style="background:{col}"></span>{nt.title()}</span>'
        for nt, col in NT_COLORS.items()
    )
    legend_shape = """
        <span class="legend-item">&#9651; Sensory</span>
        <span class="legend-item">&#9675; Interneuron</span>
        <span class="legend-item">&#9671; Modulatory</span>
        <span class="legend-item">&#9633; Motor/Output</span>
    """

    html = f'''<!DOCTYPE html>
<html lang="en"><head>
<meta charset="utf-8"><title>{title}</title>
<style>
    * {{ margin: 0; padding: 0; box-sizing: border-box; }}
    body {{ font: 14px/1.5 system-ui, -apple-system, sans-serif; background: #0f1117; color: #e0e0e0; }}
    .layout {{ display: flex; height: 100vh; }}
    .sidebar {{ width: 380px; background: #1a1b26; border-right: 1px solid #2d2d44; overflow-y: auto; padding: 20px; flex-shrink: 0; }}
    .main {{ flex: 1; display: flex; flex-direction: column; }}
    .toolbar {{ padding: 10px 20px; background: #1a1b26; border-bottom: 1px solid #2d2d44; display: flex; align-items: center; gap: 16px; }}
    .svg-container {{ flex: 1; overflow: hidden; position: relative; }}
    svg {{ width: 100%; height: 100%; }}
    h1 {{ font-size: 18px; margin-bottom: 4px; color: #fff; }}
    h2 {{ font-size: 14px; color: #888; text-transform: uppercase; margin: 20px 0 10px; letter-spacing: 0.5px; }}
    .subtitle {{ color: #888; font-size: 12px; margin-bottom: 16px; }}
    .legend {{ display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 8px; }}
    .legend-item {{ font-size: 12px; color: #aaa; display: flex; align-items: center; gap: 4px; }}
    .legend-dot {{ width: 10px; height: 10px; border-radius: 50%; display: inline-block; }}
    .neuron {{ cursor: pointer; transition: filter 0.2s; }}
    .neuron:hover {{ filter: brightness(1.5) drop-shadow(0 0 8px rgba(255,255,255,0.3)); }}
    .neuron-label {{ font-size: 11px; fill: #ccc; pointer-events: none; }}
    .conn-label {{ font-size: 9px; fill: #888; pointer-events: none; }}
    .connection {{ cursor: pointer; transition: stroke-opacity 0.2s; }}
    .connection:hover {{ stroke-opacity: 1; stroke-width: 3; }}
    .hypothesis {{ background: #252542; border-radius: 8px; padding: 12px; margin-bottom: 10px; }}
    .hypothesis p {{ margin: 6px 0; font-size: 13px; }}
    .conf-badge {{ font-size: 10px; padding: 2px 8px; border-radius: 10px; color: #fff; text-transform: uppercase; font-weight: 600; }}
    .evidence {{ color: #777; font-size: 11px; }}
    .citations {{ list-style: none; padding: 0; }}
    .citations li {{ padding: 6px 0; border-bottom: 1px solid #2d2d44; font-size: 12px; }}
    .citations li strong {{ color: #aaa; }}
    .tooltip {{ position: absolute; background: #252542; border: 1px solid #3d3d5c; border-radius: 6px; padding: 10px; font-size: 12px; pointer-events: none; white-space: pre-line; z-index: 100; max-width: 300px; display: none; }}
    .detail-panel {{ display: none; background: #252542; border-radius: 8px; padding: 14px; margin-bottom: 10px; }}
    .detail-panel.active {{ display: block; }}
    .detail-panel h3 {{ font-size: 14px; color: #fff; margin-bottom: 8px; }}
    .detail-row {{ display: flex; justify-content: space-between; padding: 4px 0; font-size: 12px; border-bottom: 1px solid #2d2d44; }}
    .detail-row .label {{ color: #888; }}
    .detail-row .value {{ color: #e0e0e0; text-align: right; max-width: 200px; }}
    button {{ background: #3d3d5c; border: none; color: #ccc; padding: 6px 14px; border-radius: 4px; cursor: pointer; font-size: 12px; }}
    button:hover {{ background: #4d4d6c; }}
    button.active {{ background: #6366f1; color: #fff; }}
</style>
</head><body>
<div class="layout">
    <div class="sidebar">
        <h1>{title}</h1>
        <p class="subtitle">Generated from VFB connectivity data</p>

        <div id="detail-panel" class="detail-panel"></div>

        <h2>Legend — Neurotransmitters</h2>
        <div class="legend">{legend_nt}</div>
        <h2>Legend — Neuron Types</h2>
        <div class="legend">{legend_shape}</div>

        <h2>Functional Hypotheses</h2>
        {hyp_html if hyp_html else '<p style="color:#666;font-size:13px;">No hypotheses generated.</p>'}

        <h2>Citations</h2>
        <ul class="citations">{cit_html if cit_html else '<li style="color:#666;">No citations.</li>'}</ul>
    </div>
    <div class="main">
        <div class="toolbar">
            <button onclick="resetView()">Reset View</button>
            <button id="btn-labels" class="active" onclick="toggleLabels()">Labels</button>
            <span style="color:#666;font-size:12px;margin-left:auto;">{len(neurons)} neurons &middot; {len(connections)} connections</span>
        </div>
        <div class="svg-container" id="svg-container">
            <svg id="circuit" viewBox="0 0 1000 700" xmlns="http://www.w3.org/2000/svg">
                <defs>
                    <marker id="arrow-exc" viewBox="0 0 10 10" refX="10" refY="5" markerWidth="8" markerHeight="8" orient="auto-start-reverse">
                        <path d="M0,0 L10,5 L0,10 Z" fill="#4CAF50"/>
                    </marker>
                    <marker id="arrow-inh" viewBox="0 0 10 10" refX="10" refY="5" markerWidth="8" markerHeight="8" orient="auto-start-reverse">
                        <circle cx="5" cy="5" r="4" fill="#E53935"/>
                    </marker>
                </defs>
                <g id="connections">{"".join(conn_svgs)}</g>
                <g id="neurons">{"".join(neuron_svgs)}</g>
            </svg>
            <div class="tooltip" id="tooltip"></div>
        </div>
    </div>
</div>
<script>
const data = {json.dumps(data, indent=2)};
const neuronMap = {{}};
data.neurons.forEach(n => neuronMap[n.id] = n);

// Tooltip
const tooltip = document.getElementById('tooltip');
const container = document.getElementById('svg-container');
document.querySelectorAll('[data-tooltip]').forEach(el => {{
    el.addEventListener('mouseenter', e => {{
        tooltip.textContent = el.getAttribute('data-tooltip').replace(/\\\\n/g, '\\n');
        tooltip.style.display = 'block';
    }});
    el.addEventListener('mousemove', e => {{
        const rect = container.getBoundingClientRect();
        tooltip.style.left = (e.clientX - rect.left + 12) + 'px';
        tooltip.style.top = (e.clientY - rect.top + 12) + 'px';
    }});
    el.addEventListener('mouseleave', () => {{ tooltip.style.display = 'none'; }});
}});

// Click neuron for detail panel
document.querySelectorAll('.neuron').forEach(el => {{
    el.addEventListener('click', () => {{
        const nid = el.getAttribute('data-id');
        const n = neuronMap[nid];
        if (!n) return;
        const panel = document.getElementById('detail-panel');
        const incoming = data.connections.filter(c => c.target === nid);
        const outgoing = data.connections.filter(c => c.source === nid);
        panel.innerHTML = `
            <h3>${{n.name}}</h3>
            <div class="detail-row"><span class="label">Type</span><span class="value">${{n.type || 'unknown'}}</span></div>
            <div class="detail-row"><span class="label">Neurotransmitter</span><span class="value">${{n.neurotransmitter || 'unknown'}} (${{n.nt_evidence || '?'}})</span></div>
            <div class="detail-row"><span class="label">Receptors</span><span class="value">${{(n.receptors||[]).join(', ') || 'unknown'}}</span></div>
            <div class="detail-row"><span class="label">Region</span><span class="value">${{n.brain_region || 'unknown'}}</span></div>
            <div class="detail-row"><span class="label">Function</span><span class="value">${{n.known_function || 'unknown'}}</span></div>
            <div class="detail-row"><span class="label">Inputs</span><span class="value">${{incoming.length}} connections</span></div>
            <div class="detail-row"><span class="label">Outputs</span><span class="value">${{outgoing.length}} connections</span></div>
        `;
        panel.classList.add('active');
    }});
}});

// Toggle labels
let labelsVisible = true;
function toggleLabels() {{
    labelsVisible = !labelsVisible;
    document.querySelectorAll('.neuron-label, .conn-label').forEach(el => {{
        el.style.display = labelsVisible ? '' : 'none';
    }});
    document.getElementById('btn-labels').classList.toggle('active', labelsVisible);
}}

// Pan/zoom
const svg = document.getElementById('circuit');
let viewBox = {{ x: 0, y: 0, w: 1000, h: 700 }};
let isPanning = false, startPoint = {{}};
svg.addEventListener('wheel', e => {{
    e.preventDefault();
    const scale = e.deltaY > 0 ? 1.1 : 0.9;
    const rect = svg.getBoundingClientRect();
    const mx = (e.clientX - rect.left) / rect.width * viewBox.w + viewBox.x;
    const my = (e.clientY - rect.top) / rect.height * viewBox.h + viewBox.y;
    viewBox.w *= scale; viewBox.h *= scale;
    viewBox.x = mx - (e.clientX - rect.left) / rect.width * viewBox.w;
    viewBox.y = my - (e.clientY - rect.top) / rect.height * viewBox.h;
    svg.setAttribute('viewBox', `${{viewBox.x}} ${{viewBox.y}} ${{viewBox.w}} ${{viewBox.h}}`);
}});
svg.addEventListener('mousedown', e => {{ isPanning = true; startPoint = {{ x: e.clientX, y: e.clientY }}; }});
svg.addEventListener('mousemove', e => {{
    if (!isPanning) return;
    const rect = svg.getBoundingClientRect();
    const dx = (e.clientX - startPoint.x) / rect.width * viewBox.w;
    const dy = (e.clientY - startPoint.y) / rect.height * viewBox.h;
    viewBox.x -= dx; viewBox.y -= dy;
    svg.setAttribute('viewBox', `${{viewBox.x}} ${{viewBox.y}} ${{viewBox.w}} ${{viewBox.h}}`);
    startPoint = {{ x: e.clientX, y: e.clientY }};
}});
svg.addEventListener('mouseup', () => {{ isPanning = false; }});
svg.addEventListener('mouseleave', () => {{ isPanning = false; }});

function resetView() {{
    viewBox = {{ x: 0, y: 0, w: 1000, h: 700 }};
    svg.setAttribute('viewBox', '0 0 1000 700');
}}
</script>
</body></html>'''
    output.write_text(html)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: circuit_diagram.py <circuit_data.json> [output.html]")
        sys.exit(1)

    data = load_data(sys.argv[1])
    out = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("circuit_diagram.html")
    generate_html(data, out)
    print(f"Generated {out.absolute()}")
    webbrowser.open(f"file://{out.absolute()}")
