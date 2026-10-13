#!/usr/bin/env python3
"""Render a prepared VFB video work folder to MP4 (frame by frame, no audio).

usage: render_video.py WORKDIR OUT.mp4 [--seconds N]
       render_video.py WORKDIR --stills 2,8,16     (JPEG previews into WORKDIR/stills, takes seconds)
"""
import argparse, functools, http.server, json, pathlib, shutil, subprocess, sys, threading


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("workdir"); ap.add_argument("output", nargs="?")
    ap.add_argument("--stills", help="comma-separated times in seconds")
    ap.add_argument("--seconds", type=float, help="render only the first N seconds")
    a = ap.parse_args(argv)
    work = pathlib.Path(a.workdir).resolve()
    if not (work / "spec.resolved.json").exists():
        print("No spec.resolved.json in that folder - run prepare.py first."); return 2
    if not a.stills and not a.output:
        ap.error("give an output .mp4 or --stills")
    if not a.stills and shutil.which("ffmpeg") is None:
        print("ffmpeg not found. Install it (brew install ffmpeg / sudo apt install ffmpeg) and retry."); return 2
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("Playwright is not installed in this Python. Run scripts/setup_video.py first."); return 2

    spec = json.load(open(work / "spec.resolved.json"))
    W, H, FPS = int(spec.get("width", 1920)), int(spec.get("height", 1080)), int(spec.get("fps", 30))
    DUR = float(a.seconds or spec.get("duration", 24))

    class Quiet(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *args): pass
    srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), functools.partial(Quiet, directory=str(work)))
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    port = srv.server_address[1]
    try:
        with sync_playwright() as p:
            try:
                b = p.chromium.launch(args=["--enable-unsafe-swiftshader"])
            except Exception as e:
                print(f"Could not start Chromium ({e}). Run scripts/setup_video.py first."); return 2
            pg = b.new_page(viewport={"width": W, "height": H})
            pg.on("console", lambda m: print("page:", m.text) if m.type == "error" else None)
            pg.on("pageerror", lambda e: print("page error:", e))
            pg.goto(f"http://127.0.0.1:{port}/index.html")
            try:
                pg.wait_for_function("window.READY===true", timeout=300000)
            except Exception:
                print("The scene did not load - see 'page:' errors above (usually a bad or empty swc/obj file)."); return 1
            if a.stills:
                (work / "stills").mkdir(exist_ok=True)
                for t in a.stills.split(","):
                    pg.evaluate(f"seek({float(t)})")
                    f = work / "stills" / f"t{float(t):06.2f}.jpg"
                    pg.screenshot(path=str(f), type="jpeg", quality=90); print(f)
            else:
                ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "image2pipe", "-framerate", str(FPS),
                                       "-c:v", "mjpeg", "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "18",
                                       "-pix_fmt", "yuv420p", "-movflags", "+faststart", a.output], stdin=subprocess.PIPE)
                n = int(DUR * FPS)
                for i in range(n):
                    pg.evaluate(f"seek({i / FPS})")
                    ff.stdin.write(pg.screenshot(type="jpeg", quality=95))
                    if i % (FPS * 5) == 0: print(f"{i / FPS:5.1f}s / {DUR:.0f}s", flush=True)
                ff.stdin.close(); rc = ff.wait()
                if rc: print("ffmpeg failed"); return rc
                print("wrote", a.output)
            b.close()
    finally:
        srv.shutdown()
    return 0


if __name__ == "__main__":
    sys.exit(main())
