#!/usr/bin/env python3
"""Render a prepared VFB video work folder to MP4 (deterministic frame-by-frame, no audio).

usage: render_video.py WORKDIR out.mp4 [--stills 1,5,20] [--seconds N]
--stills renders only those timestamps as JPEGs into WORKDIR/stills (fast preview).
"""
import functools, http.server, json, pathlib, subprocess, sys, threading
from playwright.sync_api import sync_playwright

def main():
    a = sys.argv[1:]
    if len(a) < 2 and "--stills" not in a: raise SystemExit(__doc__)
    work = pathlib.Path(a[0]).resolve(); out = a[1] if len(a) > 1 and not a[1].startswith("--") else None
    stills = a[a.index("--stills") + 1].split(",") if "--stills" in a else None
    spec = json.load(open(work / "spec.resolved.json"))
    W, H, FPS, DUR = spec.get("width", 1920), spec.get("height", 1080), spec.get("fps", 30), float(spec.get("duration", 30))
    if "--seconds" in a: DUR = float(a[a.index("--seconds") + 1])
    class Quiet(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *args): pass
    handler = functools.partial(Quiet, directory=str(work))
    srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler); port = srv.server_address[1]
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    with sync_playwright() as p:
        b = p.chromium.launch(args=["--enable-unsafe-swiftshader", "--ignore-gpu-blocklist", "--use-gl=swiftshader"] )
        pg = b.new_page(viewport={"width": W, "height": H})
        pg.on("console", lambda m: print("page:", m.text) if m.type == "error" else None)
        pg.goto(f"http://127.0.0.1:{port}/index.html"); pg.wait_for_function("window.READY===true", timeout=300000)
        if stills:
            (work / "stills").mkdir(exist_ok=True)
            for t in stills:
                pg.evaluate(f"seek({float(t)})"); f = work / "stills" / f"t{float(t):06.2f}.jpg"; pg.screenshot(path=str(f), type="jpeg", quality=90); print(f)
        else:
            ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "image2pipe", "-framerate", str(FPS), "-c:v", "mjpeg", "-i", "-",
                                   "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", out], stdin=subprocess.PIPE)
            n = int(DUR * FPS)
            for i in range(n):
                pg.evaluate(f"seek({i / FPS})"); ff.stdin.write(pg.screenshot(type="jpeg", quality=95))
                if i % (FPS * 5) == 0: print(f"{i / FPS:5.1f}s / {DUR:.0f}s", flush=True)
            ff.stdin.close(); ff.wait(); print("wrote", out)
        b.close()
    srv.shutdown()

if __name__ == "__main__": main()
