"""Publication checks for reviewed synthetic screenshots, using generated pixels."""

import contextlib
import hashlib
import io
import json
import struct
import sys
import tempfile
import unittest
import zlib
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import repo_checks


def chunk(kind, body):
    return struct.pack(">I", len(body)) + kind + body + struct.pack(">I", zlib.crc32(kind + body) & 0xFFFFFFFF)


def png(width=64, height=64, before_data=b"", raster=None):
    header = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
    pixels = raster if raster is not None else (b"\0" + b"\x40\x50\x60" * width) * height
    return repo_checks.PNG_SIGNATURE + chunk(b"IHDR", header) + before_data + chunk(b"IDAT", zlib.compress(pixels)) + chunk(b"IEND", b"")


def media(raw=None, name="docs/assets/showcase-desktop.png"):
    raw = png() if raw is None else raw
    manifest = {
        "schema_version": "factorio-bench.public-media.v1",
        "assets": [{
            "path": name,
            "sha256": hashlib.sha256(raw).hexdigest(),
            "width": 64,
            "height": 64,
            "provenance": "Synthetic test pixels; no game content or private records.",
            "reviewed": True,
        }],
    }
    return {name: raw, repo_checks.MEDIA_MANIFEST: (json.dumps(manifest, indent=2) + "\n").encode()}


class MediaPolicyTests(unittest.TestCase):
    def test_valid_reviewed_rgb_and_rgba_screenshots_are_accepted(self):
        self.assertEqual(repo_checks.media_problems(media()), [])
        rgba = repo_checks.PNG_SIGNATURE + chunk(b"IHDR", struct.pack(">IIBBBBB", 64, 64, 8, 6, 0, 0, 0))
        rgba += chunk(b"IDAT", zlib.compress((b"\0" + b"\x40\x50\x60\xff" * 64) * 64)) + chunk(b"IEND", b"")
        self.assertEqual(repo_checks.media_problems(media(rgba)), [])

    def test_unlisted_paths_and_missing_manifests_are_rejected(self):
        for name in ("docs/other.png", "docs/assets/other.png", "docs/assets/showcase-desktop.PNG"):
            with self.subTest(name=name):
                self.assertTrue(repo_checks.media_problems(media(name=name)))
        self.assertTrue(repo_checks.media_problems({"docs/assets/showcase-desktop.png": png()}))
        files = media()
        files["extra.png"] = png()
        self.assertTrue(repo_checks.media_problems(files))

    def test_manifest_must_match_digest_dimensions_and_review(self):
        for field, value in (("sha256", "0" * 64), ("width", 65), ("height", True), ("reviewed", False), ("provenance", "")):
            with self.subTest(field=field):
                files = media()
                manifest = json.loads(files[repo_checks.MEDIA_MANIFEST])
                manifest["assets"][0][field] = value
                files[repo_checks.MEDIA_MANIFEST] = json.dumps(manifest).encode()
                self.assertTrue(repo_checks.media_problems(files))

    def test_duplicate_missing_and_malformed_manifest_entries_fail(self):
        for replacement in (None, [], {}, {"schema_version": "unknown", "assets": []}):
            files = media()
            files[repo_checks.MEDIA_MANIFEST] = json.dumps(replacement).encode()
            self.assertTrue(repo_checks.media_problems(files))
        files = media()
        manifest = json.loads(files[repo_checks.MEDIA_MANIFEST])
        manifest["assets"] *= 2
        files[repo_checks.MEDIA_MANIFEST] = json.dumps(manifest).encode()
        self.assertTrue(repo_checks.media_problems(files))
        self.assertTrue(repo_checks.media_problems({repo_checks.MEDIA_MANIFEST: media()[repo_checks.MEDIA_MANIFEST]}))

    def test_metadata_unknown_chunks_and_trailing_payloads_are_rejected(self):
        fixtures = [
            png(before_data=chunk(b"tEXt", b"Comment\0synthetic metadata")),
            png(before_data=chunk(b"iTXt", b"synthetic metadata")),
            png(before_data=chunk(b"eXIf", b"synthetic metadata")),
            png(before_data=chunk(b"sRGB", b"\0")),
            png() + b"synthetic trailing payload",
        ]
        for raw in fixtures:
            with self.subTest(size=len(raw)):
                self.assertTrue(repo_checks.media_problems(media(raw)))

    def test_corruption_invalid_dimensions_and_oversized_rasters_are_rejected(self):
        corrupted = bytearray(png())
        corrupted[-1] ^= 1
        fixtures = [
            bytes(corrupted), png()[:-5], png(width=63), png(height=4097),
            png(raster=b"\0" * (64 * 193 + 1)), png(raster=b"\5" + b"\0" * (64 * 193 - 1)),
            png() + b"\0" * repo_checks.MAX_PNG_BYTES,
        ]
        for raw in fixtures:
            with self.subTest(size=len(raw)):
                self.assertTrue(repo_checks.media_problems(media(raw)))

    def test_concatenated_compressed_data_is_rejected(self):
        raw = repo_checks.PNG_SIGNATURE + chunk(b"IHDR", struct.pack(">IIBBBBB", 64, 64, 8, 2, 0, 0, 0))
        raw += chunk(b"IDAT", zlib.compress(b"\0" * (64 * 193)) + zlib.compress(b"extra")) + chunk(b"IEND", b"")
        self.assertTrue(repo_checks.media_problems(media(raw)))

    def test_replacement_in_working_tree_cannot_hide_staged_media(self):
        with tempfile.TemporaryDirectory(prefix="factorio-bench-media-test-") as temporary:
            root = Path(temporary)
            repo_checks.git(root, "init", "--quiet")
            files = media()
            for name, raw in files.items():
                path = root / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(raw)
            name = "docs/assets/showcase-desktop.png"
            (root / name).write_bytes(png(before_data=chunk(b"tEXt", b"Comment\0synthetic metadata")))
            repo_checks.git(root, "add", name, repo_checks.MEDIA_MANIFEST)
            (root / name).write_bytes(files[name])
            self.assertEqual(repo_checks.media_problems(files), [])
            self.assertTrue(repo_checks.media_problems(repo_checks.indexed_media(root)))
            output = io.StringIO()
            with contextlib.redirect_stdout(output), contextlib.redirect_stderr(output):
                self.assertEqual(repo_checks.check(root), 1)
            self.assertNotIn("synthetic metadata", output.getvalue())


if __name__ == "__main__":
    unittest.main()
