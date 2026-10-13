import json, pathlib, pytest
import prepare

EX = pathlib.Path(__file__).resolve().parents[1] / "example" / "spec.json"


def spec():
    return json.load(open(EX))


def test_example_spec_is_valid():
    assert prepare.validate_spec(spec())


@pytest.mark.parametrize("url", ["http://www.virtualflybrain.org/data/x.swc", "https://evil.example/data/x.swc",
                                 "https://www.virtualflybrain.org.evil.example/data/x.swc", "file:///etc/passwd", None])
def test_only_vfb_https_urls_allowed(url):
    s = spec(); s["items"][0]["swc"] = url
    with pytest.raises(prepare.SpecError):
        prepare.validate_spec(s)


@pytest.mark.parametrize("bad", ["../x", "a/b", "VFB 1", "", "x" * 50, None])
def test_ids_are_filename_safe(bad):
    s = spec(); s["items"][0]["id"] = bad
    with pytest.raises(prepare.SpecError):
        prepare.validate_spec(s)


@pytest.mark.parametrize("key,val", [("width", 10), ("fps", 500), ("duration", 9999), ("zoom_out", 0)])
def test_numeric_limits(key, val):
    s = spec(); s[key] = val
    with pytest.raises(prepare.SpecError):
        prepare.validate_spec(s)


def test_item_count_and_colour():
    s = spec(); s["items"] = []
    with pytest.raises(prepare.SpecError):
        prepare.validate_spec(s)
    s = spec(); s["items"][0]["color"] = "red; background:url(x)"
    with pytest.raises(prepare.SpecError):
        prepare.validate_spec(s)


def test_references_always_cite_vfb_and_datasets():
    refs, ack, end, warn, today, sources = prepare.build_references(spec(), today="2026-01-01")
    text = " ".join(r["apa"] for r in refs)
    assert "10.3389/fphys.2023.1076533" in text and "10.64898/2026.06.16.732577" in text
    assert "accessed 2026-01-01" in ack and "EM FAFB Zheng et al 2018" in ack
    assert len(end) <= 7 and any("virtualflybrain.org" in l for l in end)


def test_mcp_citation_only_when_used():
    s = spec(); s["used_mcp"] = False
    refs, ack, *_ = prepare.build_references(s)
    assert "VFB-MCP" not in " ".join(r["apa"] for r in refs) and "MCP" not in ack


def test_non_commercial_licence_warns():
    _, _, _, warn, _, _ = prepare.build_references(spec())
    assert any("non-commercial" in w for w in warn)


def test_missing_licence_is_flagged():
    s = spec(); s["items"][0]["licenses"] = [{"source": "Some dataset", "label": ""}]
    _, _, _, warn, _, _ = prepare.build_references(s)
    assert any("no licence recorded" in w for w in warn)


def test_end_card_truncates_with_pointer():
    s = spec(); s["items"][0]["publications"] = [{"citation": f"Paper {i}", "doi": ""} for i in range(10)]
    end = prepare.build_references(s)[2]
    assert len(end) == 7 and "references.md" in end[-1]


def test_item_without_any_licence_warns():
    s = spec(); s["items"][0]["licenses"] = []
    _, _, _, warn, _, _ = prepare.build_references(s)
    assert any("VFB_00101199 has no licence information" in w for w in warn)
