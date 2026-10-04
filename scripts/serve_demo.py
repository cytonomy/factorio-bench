#!/usr/bin/env python3
"""Serve only the public showcase assets, on loopback, without request logs."""

import argparse
import mimetypes
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1] / "showcase"
PUBLIC_FILES = {"index.html", "style.css", "app.js", "favicon.svg", "data/examples.json"}


class DemoHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.serve(head=False)

    def do_HEAD(self):
        self.serve(head=True)

    def serve(self, head):
        route = urlsplit(self.path).path.lstrip("/") or "index.html"
        if route not in PUBLIC_FILES:
            self.send_error(404)
            return
        path = ROOT / route
        if not path.is_file() or path.is_symlink() or not path.resolve().is_relative_to(ROOT.resolve()):
            self.send_error(404)
            return
        data = path.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", mimetypes.guess_type(path.name)[0] or "application/octet-stream")
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header("Content-Security-Policy", "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self'; connect-src 'self'; frame-ancestors 'none'; base-uri 'none'")
        self.end_headers()
        if not head:
            self.wfile.write(data)

    def log_message(self, format, *args):
        pass


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args()
    if not 1024 <= args.port <= 65535:
        parser.error("port must be between 1024 and 65535")
    try:
        with ThreadingHTTPServer(("127.0.0.1", args.port), DemoHandler) as server:
            print(f"Evidence lab: http://127.0.0.1:{args.port} (Ctrl+C to stop)", flush=True)
            server.serve_forever()
    except KeyboardInterrupt:
        print("\nEvidence lab stopped.")
    except OSError:
        parser.exit(1, "Could not start the local server. Try --port with a different port.\n")


if __name__ == "__main__":
    main()
