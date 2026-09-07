"""Tests for the vfb-3d-viewer build script.

Offline unit tests run anywhere; the live integration test builds a real viewer
against virtualflybrain.org and is skipped when offline.
"""
import importlib.util
import json
import os
import socket
import subprocess
import sys
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPTS = os.path.join(HERE, "..", "scripts")
BUILD = os.path.join(SCRIPTS, "build_viewer.py")
TEMPLATE = os.path.join(SCRIPTS, "viewer_template.html")

import pytest  # noqa: E402

# import build_viewer as a module
spec = importlib.util.spec_from_file_location("build_viewer", BUILD)
bv = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bv)


def _online(host="www.virtualflybrain.org", port=443, timeout=4):
    try:
        socket.create_connection((host, port), timeout=timeout).close()
        return True
    except OSError:
        return False


# ---- offline unit tests ---------------------------------------------------

def test_id_to_path_neuron():
    assert bv.id_to_path("VFB_jrmc02fh") == ("jrmc", "02fh")


def test_id_to_path_template():
    assert bv.id_to_path("VFB_00200000") == ("0020", "0000")


def test_id_to_path_without_prefix():
    assert bv.id_to_path("jrcv07tf") == ("jrcv", "07tf")


def test_id_to_path_rejects_short():
    with pytest.raises(ValueError):
        bv.id_to_path("VFB_123")


def test_swc_url_uses_template_space():
    url = bv.swc_url("VFB_jrmc02fh", "VFB_00200000")
    assert url.endswith("/jrmc/02fh/VFB_00200000/volume.swc")


def test_obj_url():
    url = bv.obj_url("VFB_00200000")
    assert url.endswith("/0020/0000/VFB_00200000/volume_man.obj")


def test_parse_swc():
    text = "# comment\n1 0 10 20 30 0.5 -1\n2 0 11 21 31 0.5 1\n"
    raw, remap = bv.parse_swc(text)
    assert raw[1] == (10.0, 20.0, 30.0, -1)
    assert raw[2][3] == 1
    assert remap == {1: 0, 2: 1}


def test_template_has_all_placeholders():
    html = open(TEMPLATE).read()
    for token in ("/*NEURON_DATA*/", "/*TMPL_DATA*/", "/*TITLE*/",
                  "/*SUBTITLE*/", "/*PAGE_TITLE*/", "/*CREDIT*/"):
        assert token in html, "template missing " + token


# ---- live integration test ------------------------------------------------

@pytest.mark.skipif(not _online(), reason="offline: skipping live VFB build")
def test_build_b2_viewer(tmp_path):
    spec_path = tmp_path / "spec.json"
    out_path = tmp_path / "viewer.html"
    spec_path.write_text(json.dumps({
        "title": "b2 motor neurons (test)",
        "template": {"id": "VFB_00200000", "label": "JRCVNC2018U",
                     "render_mesh": False},   # skip the big OBJ to keep the test light
        "neurons": [
            {"id": "VFB_jrmc02fh", "label": "b2 MN_L"},
            {"id": "VFB_jrmc02fg", "label": "b2 MN_R"},
        ],
    }))
    r = subprocess.run(
        [sys.executable, BUILD, "--spec", str(spec_path), "--out", str(out_path)],
        capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    html = out_path.read_text()
    # data injected, placeholders gone, both neurons present
    assert "/*NEURON_DATA*/" not in html
    assert '"key":"VFB_jrmc02fh"' in html
    assert '"key":"VFB_jrmc02fg"' in html
    assert "<title>b2 motor neurons (test)</title>" in html
    # template mesh was disabled -> empty tmpl block, button hidden path
    assert '<script id="tmpl" type="application/json"></script>' in html
