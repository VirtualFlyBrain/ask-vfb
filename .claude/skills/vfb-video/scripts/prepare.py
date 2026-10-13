#!/usr/bin/env python3
"""Prepare a VFB video work folder: validate the spec, download geometry, build the reference text.

usage: prepare.py spec.json WORKDIR

Writes WORKDIR/{index.html, vendor/three.module.min.js, assets/*, spec.resolved.json, references.md}.
Only https://www.virtualflybrain.org/data/ URLs are ever downloaded (redirects included).
"""
import datetime, json, pathlib, re, shutil, sys, time, urllib.error, urllib.request

OK_PREFIX = "https://www.virtualflybrain.org/data/"
MAX_BYTES = 150 * 1024 * 1024
HERE = pathlib.Path(__file__).resolve().parent
SKILL = HERE.parent
ID_RE = re.compile(r"^[A-Za-z0-9_]{1,40}$")
COLOR_RE = re.compile(r"^#[0-9a-fA-F]{6}$")

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


class SpecError(ValueError):
    pass


def check_url(url):
    if not isinstance(url, str) or not url.startswith(OK_PREFIX):
        raise SpecError(f"only {OK_PREFIX}... URLs are allowed, got: {url!r}")
    return url


def safe_tag(vfb_id):
    if not isinstance(vfb_id, str) or not ID_RE.match(vfb_id):
        raise SpecError(f"bad id {vfb_id!r}: use letters, digits and underscores only (e.g. VFB_00101199)")
    return vfb_id


def _num(spec, key, default, lo, hi):
    v = spec.get(key, default)
    if not isinstance(v, (int, float)) or isinstance(v, bool) or not lo <= v <= hi:
        raise SpecError(f"{key} must be a number between {lo} and {hi}")
    return v


def validate_spec(spec):
    """Raise SpecError for anything unsafe or unusable; return the spec."""
    if not isinstance(spec, dict):
        raise SpecError("spec must be a JSON object")
    _num(spec, "width", 1920, 320, 3840); _num(spec, "height", 1080, 240, 2160)
    _num(spec, "fps", 30, 10, 60); _num(spec, "duration", 24, 5, 180)
    _num(spec, "zoom_out", 1.5, 0.3, 6); _num(spec, "orbit_turns", 0.6, -4, 4)
    for key in ("title", "subtitle"):
        if not isinstance(spec.get(key, ""), str) or len(spec.get(key, "")) > 200:
            raise SpecError(f"{key} must be text of at most 200 characters")
    items = spec.get("items", [])
    if not isinstance(items, list) or not 1 <= len(items) <= 12:
        raise SpecError("items must be a list of 1 to 12 entries")
    entries = list(items) + ([spec["template"]] if spec.get("template") else [])
    for it in entries:
        if not isinstance(it, dict):
            raise SpecError("each item must be an object")
        safe_tag(it.get("id"))
        if not (it.get("swc") or it.get("obj")):
            if it is not spec.get("template"):
                raise SpecError(f"{it['id']}: give a 'swc' or 'obj' URL")
        for kind in ("swc", "obj"):
            if it.get(kind):
                check_url(it[kind])
        if "label" in it and (not isinstance(it["label"], str) or len(it["label"]) > 80):
            raise SpecError(f"{it['id']}: label must be text of at most 80 characters")
        if "color" in it and not COLOR_RE.match(str(it["color"])):
            raise SpecError(f"{it['id']}: color must look like #4c8dff")
        for lic in it.get("licenses", []):
            if not isinstance(lic, dict):
                raise SpecError(f"{it['id']}: each licence must be an object with source and label")
    return spec


class _SafeRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        check_url(newurl)
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def download(url, dest):
    check_url(url)
    if dest.exists() and dest.stat().st_size > 0:
        return
    opener = urllib.request.build_opener(_SafeRedirect)
    req = urllib.request.Request(url, headers={"User-Agent": "vfb-video-skill/1.0 (+https://virtualflybrain.org)"})
    err = None
    for attempt in range(3):
        try:
            with opener.open(req, timeout=120) as r, open(dest, "wb") as f:
                total = 0
                while True:
                    chunk = r.read(1 << 20)
                    if not chunk:
                        break
                    total += len(chunk)
                    if total > MAX_BYTES:
                        raise SpecError(f"{url} is larger than {MAX_BYTES // 2**20} MB; refusing")
                    f.write(chunk)
            return
        except urllib.error.HTTPError as e:
            err = e
            if e.code in (403, 404):  # will not get better by retrying
                break
            time.sleep(2 * (attempt + 1))
        except (urllib.error.URLError, TimeoutError) as e:
            err = e; time.sleep(2 * (attempt + 1))
    dest.unlink(missing_ok=True)
    raise SystemExit(f"download failed for {url}: {err}\n"
                     "(404 usually means that file does not exist for this image/template: try the other of swc/obj.)")


def build_references(spec, today=None):
    today = today or datetime.date.today().isoformat()
    refs, warnings = [PRIMARY], []
    if spec.get("used_mcp"): refs.append(MCP)
    if spec.get("used_ontology", True): refs.append(ONTO)
    sources, pubs = {}, {}
    entries = list(spec.get("items", [])) + ([spec["template"]] if spec.get("template") else [])
    for it in entries:
        if not it.get("licenses"):
            warnings.append(f"{it.get('id')} has no licence information in the spec: copy 'Licenses' from get_term_info before sharing the video.")
        for lic in it.get("licenses", []):
            key = (str(lic.get("source", "")).strip(), str(lic.get("label", "")).strip())
            if key[0]:
                sources[key] = lic.get("source_iri", "")
            lab = key[1].upper().replace("-", "_")
            if "NC" in lab.split("_"):
                warnings.append(f"'{key[0]}' is {key[1]} (non-commercial): fine for research and teaching, not for commercial use.")
            elif key[1] and not lab.startswith("CC_BY"):
                warnings.append(f"'{key[0]}' has licence '{key[1]}': check its terms before publishing the video.")
            elif not key[1]:
                warnings.append(f"'{key[0]}' has no licence recorded: check before publishing the video.")
        for p in it.get("publications", []):
            cite = str(p.get("citation") or p.get("doi") or "").strip()
            if cite:
                pubs[cite] = str(p.get("doi", "")).strip()
    for cite, doi in pubs.items():
        refs.append({"apa": cite + (f" https://doi.org/{doi}" if doi and doi not in cite else ""), "short": cite})
    ds = "; ".join(f"{s} ({l})" if l else s for (s, l) in sorted(sources))
    ack = ("Neuron and brain-region data in this video were obtained from Virtual Fly Brain (virtualflybrain.org; "
           f"{PRIMARY['short']}), accessed {today}"
           + (f" through the VFB MCP tool ({MCP['short']})" if spec.get("used_mcp") else "") + ". "
           + (f"Underlying datasets: {ds}. " if ds else "")
           + "Please also credit the original data providers named in the dataset list.")
    end = ["Data and 3D images: Virtual Fly Brain (virtualflybrain.org)", PRIMARY["short"]]
    if spec.get("used_mcp"): end.append(MCP["short"])
    if ds: end.append("Data: " + ds)
    end += list(pubs)
    if len(end) > 7:
        end = end[:6] + ["More references: see references.md"]
    return refs, ack, end, sorted(set(warnings)), today, sources


def references_markdown(refs, ack, warnings, today, sources):
    md = ["# References and acknowledgement wording", "",
          f"Generated {today}. Paste the acknowledgement into the video description, slide notes or methods.", "",
          "## Suggested acknowledgement", "", ack, "", "## References (APA)", ""] + [f"- {r['apa']}" for r in refs]
    if sources:
        md += ["", "## Datasets used", ""] + [f"- {s} ({l}) {u}".rstrip() for (s, l), u in sorted(sources.items())]
    if warnings:
        md += ["", "## Licence notes", ""] + [f"- {w}" for w in warnings]
    return "\n".join(md) + "\n"


def main(argv):
    if len(argv) != 3:
        print(__doc__); return 2
    try:
        spec = validate_spec(json.load(open(argv[1])))
    except (OSError, json.JSONDecodeError) as e:
        print(f"cannot read spec: {e}"); return 2
    except SpecError as e:
        print(f"spec problem: {e}"); return 2
    work = pathlib.Path(argv[2]); (work / "assets").mkdir(parents=True, exist_ok=True); (work / "vendor").mkdir(exist_ok=True)
    shutil.copy(SKILL / "scene" / "vendor" / "three.module.min.js", work / "vendor" / "three.module.min.js")
    shutil.copy(SKILL / "scene" / "index.html", work / "index.html")
    for it in spec["items"] + ([spec["template"]] if spec.get("template") else []):
        for kind in ("swc", "obj"):
            if it.get(kind):
                dest = work / "assets" / f"{it['id']}.{kind}"
                download(it[kind], dest); it[f"{kind}_local"] = f"assets/{it['id']}.{kind}"
    refs, ack, end, warnings, today, sources = build_references(spec)
    spec["end_card_lines"] = end
    json.dump(spec, open(work / "spec.resolved.json", "w"), indent=1)
    (work / "references.md").write_text(references_markdown(refs, ack, warnings, today, sources), encoding="utf-8")
    print(f"prepared {work} ({len(spec['items'])} items); wording in {work / 'references.md'}")
    for w in warnings: print("NOTE:", w)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
