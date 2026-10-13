#!/usr/bin/env python3
"""Prepare a VFB video work folder: download geometry, build the reference/acknowledgement text.

usage: prepare.py spec.json WORKDIR
Writes WORKDIR/{index.html, vendor/three.module.min.js, assets/*, spec.resolved.json, references.md}
Only https://www.virtualflybrain.org/data/ URLs are downloaded.
"""
import json, os, shutil, sys, time, urllib.request, datetime, pathlib

OK_PREFIX = "https://www.virtualflybrain.org/data/"
HERE = pathlib.Path(__file__).resolve().parent
CACHE = pathlib.Path(os.environ.get("XDG_CACHE_HOME", pathlib.Path.home() / ".cache")) / "vfb-video"

PRIMARY = {
 "apa": "Court, R., Costa, M., Pilgrim, C., Millburn, G., Holmes, A., McLachlan, A., Larkin, A., Matentzoglu, N., Kir, H., Parkinson, H., Brown, N. H., O'Kane, C. J., Armstrong, J. D., Jefferis, G. S. X. E., & Osumi-Sutherland, D. (2023). Virtual Fly Brain—An interactive atlas of the Drosophila nervous system. Frontiers in Physiology, 14. https://doi.org/10.3389/fphys.2023.1076533",
 "short": "Court et al. 2023, Front. Physiol. 14:1076533 (doi:10.3389/fphys.2023.1076533)",
}
MCP = {
 "apa": "McLachlan, A. D., Court, R., Pilgrim, C., Longden, K., Brown, N. H., Osumi-Sutherland, D., Jefferis, G. S. X. E., & Armstrong, J. D. (2026). VFB-MCP: Natural-language access to Drosophila neuroscience grounded by an expert-curated ontology-led knowledgebase [Preprint]. bioRxiv. https://doi.org/10.64898/2026.06.16.732577",
 "short": "McLachlan et al. 2026, bioRxiv (doi:10.64898/2026.06.16.732577)",
}
ONTO = {
 "apa": "Osumi-Sutherland, D., Reeve, S., Mungall, C. J., Neuhaus, F., Ruttenberg, A., Jefferis, G. S., & Armstrong, J. D. (2012). A strategy for building neuroanatomy ontologies. Bioinformatics, 28(9). https://doi.org/10.1093/bioinformatics/bts113",
 "short": "Osumi-Sutherland et al. 2012, Bioinformatics (doi:10.1093/bioinformatics/bts113)",
}

def get(url, dest):
    if not url.startswith(OK_PREFIX):
        raise SystemExit(f"refusing to download non-VFB URL: {url}")
    if dest.exists() and dest.stat().st_size > 0:
        return
    for attempt in range(3):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'vfb-video-skill/1.0 (+https://virtualflybrain.org)'})
            with urllib.request.urlopen(req, timeout=120) as r, open(dest, "wb") as f:
                shutil.copyfileobj(r, f)
            return
        except Exception as e:
            err = e; time.sleep(2 * (attempt + 1))
    raise SystemExit(f"download failed: {url}: {err}")

def build_references(spec):
    today = datetime.date.today().isoformat()
    refs, warnings = [PRIMARY], []
    if spec.get("used_mcp"): refs.append(MCP)
    if spec.get("used_ontology", True): refs.append(ONTO)
    sources, pubs = {}, {}
    entries = list(spec.get("items", [])) + ([spec["template"]] if spec.get("template") else [])
    for it in entries:
        for lic in it.get("licenses", []):
            key = (lic.get("source", "").strip(), lic.get("label", "").strip())
            if key[0]: sources[key] = lic.get("source_iri", "")
            lab = key[1].upper().replace("-", "_")
            if "NC" in lab.split("_") or "NC" in lab:
                warnings.append(f"'{key[0]}' is {key[1]} (non-commercial): fine for research/teaching, not for commercial use.")
            if not lab.startswith("CC_BY") and key[1]:
                warnings.append(f"'{key[0]}' has licence '{key[1]}' - check its terms before publishing the video.")
        for p in it.get("publications", []):
            pubs[p.get("citation") or p.get("doi", "")] = p
    for k, p in pubs.items():
        if k: refs.append({"apa": k + (f" https://doi.org/{p['doi']}" if p.get("doi") and p["doi"] not in k else ""), "short": k})
    data_line = "Data: " + "; ".join(f"{s} ({l})" if l else s for (s, l) in sorted(sources)) if sources else ""
    ack = ("Neuron and brain-region data in this video were obtained from Virtual Fly Brain (virtualflybrain.org; "
           f"{PRIMARY['short']}), accessed {today}"
           + (f" through the VFB MCP tool ({MCP['short']})" if spec.get("used_mcp") else "")
           + ". "
           + (("Underlying datasets: " + "; ".join(f"{s} ({l})" if l else s for (s, l) in sorted(sources)) + ". ") if sources else "")
           + "Please also acknowledge the original data providers listed above.")
    end = ["Data and 3D images: Virtual Fly Brain (virtualflybrain.org)", PRIMARY["short"]]
    if spec.get("used_mcp"): end.append(MCP["short"])
    if data_line: end.append(data_line)
    for k, p in pubs.items():
        if k: end.append(k)
    return refs, ack, end, warnings, today, sources

def main():
    if len(sys.argv) != 3: raise SystemExit(__doc__)
    spec = json.load(open(sys.argv[1])); work = pathlib.Path(sys.argv[2]); (work / "assets").mkdir(parents=True, exist_ok=True)
    (work / "vendor").mkdir(exist_ok=True)
    three = CACHE / "three.module.min.js"
    if not three.exists(): raise SystemExit("three.js not cached - run scripts/setup_video.sh first")
    shutil.copy(three, work / "vendor" / "three.module.min.js")
    shutil.copy(HERE.parent / "scene" / "index.html", work / "index.html")
    for it in spec.get("items", []) + ([spec["template"]] if spec.get("template") else []):
        tag = it["id"].replace("/", "_")
        for kind in ("swc", "obj"):
            if it.get(kind):
                dest = work / "assets" / f"{tag}.{kind}"; get(it[kind], dest); it[f"{kind}_local"] = f"assets/{tag}.{kind}"
    refs, ack, end, warnings, today, sources = build_references(spec)
    spec["end_card_lines"] = end[:7]
    json.dump(spec, open(work / "spec.resolved.json", "w"), indent=1)
    md = ["# References and acknowledgement wording", "", f"Generated {today}. Paste the acknowledgement into your video description, slide notes or methods.", "",
          "## Suggested acknowledgement", "", ack, "", "## References (APA)", ""] + [f"- {r['apa']}" for r in refs]
    if sources: md += ["", "## Datasets used", ""] + [f"- {sn} ({lb}) {u}".rstrip() for (sn, lb), u in sorted(sources.items())]
    if warnings: md += ["", "## Licence notes", ""] + [f"- {w}" for w in sorted(set(warnings))]
    open(work / "references.md", "w").write("\n".join(md) + "\n")
    print(f"prepared {work}  ({len(spec.get('items', []))} items)  -> references.md")
    for w in sorted(set(warnings)): print("NOTE:", w)

if __name__ == "__main__": main()
