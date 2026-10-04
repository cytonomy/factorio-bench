"""Exercise the showcase HTTP boundary without opening a network socket."""

import contextlib
import io
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import serve_demo


class MemoryConnection:
    def __init__(self, request):
        self.input = io.BytesIO(request)
        self.output = io.BytesIO()

    def makefile(self, mode, *args):
        return self.input

    def sendall(self, data):
        self.output.write(data)


class DemoServerTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="factorio-bench-http-test-")
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name) / "showcase"
        self.root.mkdir()
        (self.root / "index.html").write_text("<p>Synthetic example</p>\n", encoding="utf-8")
        (self.root / "data").mkdir()
        (self.root / "data" / "examples.json").write_text("{}\n", encoding="utf-8")
        self.root_patch = patch.object(serve_demo, "ROOT", self.root)
        self.root_patch.start()
        self.addCleanup(self.root_patch.stop)

    def request(self, path, method="GET"):
        connection = MemoryConnection(f"{method} {path} HTTP/1.1\r\nHost: localhost\r\n\r\n".encode("ascii"))
        output, errors = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(output), contextlib.redirect_stderr(errors):
            serve_demo.DemoHandler(connection, ("127.0.0.1", 12345), object())
        self.assertEqual(output.getvalue() + errors.getvalue(), "")
        headers, _, body = connection.output.getvalue().partition(b"\r\n\r\n")
        return headers.decode("ascii"), body

    def test_allowlisted_get_head_and_query(self):
        for route in ("/", "/index.html?example=synthetic"):
            headers, body = self.request(route)
            self.assertIn("200 OK", headers)
            self.assertEqual(body, b"<p>Synthetic example</p>\n")
            self.assertIn("Cache-Control: no-store", headers)
            self.assertIn("X-Content-Type-Options: nosniff", headers)
            self.assertIn("Content-Security-Policy:", headers)
            self.assertIn("frame-ancestors 'none'", headers)
        headers, body = self.request("/data/examples.json", method="HEAD")
        self.assertIn("200 OK", headers)
        self.assertIn("Content-Length: 3", headers)
        self.assertEqual(body, b"")

    def test_private_unlisted_and_traversal_paths_are_rejected(self):
        (self.root / ".env").write_text("synthetic private marker\n", encoding="utf-8")
        (self.root / "extra.html").write_text("unreviewed content\n", encoding="utf-8")
        for route in ("/.env", "/extra.html", "/.git/config", "/../README.md", "/%2e%2e/README.md", "/data/../index.html", "/scripts/serve_demo.py", "/data/", "/missing"):
            with self.subTest(route=route):
                headers, body = self.request(route)
                self.assertIn("404 Not Found", headers)
                self.assertNotIn(b"synthetic private marker", body)
                self.assertNotIn(b"unreviewed content", body)

    def test_direct_and_parent_symlinks_cannot_expose_external_files(self):
        outside = self.root.parent / "outside"
        outside.mkdir()
        (outside / "examples.json").write_text("private fixture\n", encoding="utf-8")
        (self.root / "index.html").unlink()
        (self.root / "index.html").symlink_to(outside / "examples.json")
        headers, body = self.request("/")
        self.assertIn("404 Not Found", headers)
        self.assertNotIn(b"private fixture", body)
        (self.root / "data" / "examples.json").unlink()
        (self.root / "data").rmdir()
        (self.root / "data").symlink_to(outside, target_is_directory=True)
        headers, body = self.request("/data/examples.json")
        self.assertIn("404 Not Found", headers)
        self.assertNotIn(b"private fixture", body)


if __name__ == "__main__":
    unittest.main()
