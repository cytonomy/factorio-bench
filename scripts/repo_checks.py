#!/usr/bin/env python3
"""Small, dependency-free checks for this documentation-first repository."""

import hashlib
import json
import re
import struct
import subprocess
import sys
import zlib
from pathlib import Path, PurePosixPath
from urllib.parse import unquote, urlsplit


ROOT = Path(__file__).resolve().parents[1]
PRIVATE_DIRS = {
    ".agents", ".codex", ".claude", ".aws", ".azure", ".ssh", ".venv",
    ".vscode", ".idea", ".cache", ".tools", ".pytest_cache", ".ruff_cache",
    "__pycache__", "artifacts", "credentials", "downloads", "factorio", "logs",
    "node_modules", "private", "recordings", "results", "runs", "saves", "secrets", ".secrets",
}
PRIVATE_NAMES = {
    ".netrc", "_netrc", ".npmrc", ".pypirc", "credentials", "credentials.json",
    "player-data.json", "server-settings.json", "server-rcon-password.txt",
}
PRIVATE_SUFFIXES = {
    ".key", ".pem", ".p12", ".pfx", ".jks", ".keystore", ".log",
    ".zip", ".tar", ".gz", ".tgz", ".7z", ".rar", ".sqlite", ".sqlite3", ".db",
    ".mp4", ".webm",
}
MEDIA_MANIFEST = "docs/assets/manifest.json"
PUBLIC_PNGS = {
    "docs/assets/showcase-desktop.png",
    "docs/assets/showcase-mobile.png",
}
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
MAX_PNG_BYTES = 8 * 1024 * 1024


def git(root, *args):
    result = subprocess.run(
        ["git", "-C", str(root), *args], capture_output=True, check=False
    )
    if result.returncode:
        raise RuntimeError("Git inspection failed; diagnostic output suppressed.")
    return result.stdout


def candidates(root):
    """Tracked/index paths plus nonignored new files, including forced additions."""
    names = git(root, "ls-files", "--cached", "--others", "--exclude-standard", "-z")
    return sorted({name.decode("utf-8") for name in names.split(b"\0") if name})


def disallowed_path(name):
    parts = PurePosixPath(name).parts
    if not parts or PurePosixPath(name).is_absolute() or ".." in parts:
        return True
    lowered = [part.lower() for part in parts]
    leaf = lowered[-1]
    if any(part in PRIVATE_DIRS for part in lowered):
        return True
    if leaf in PRIVATE_NAMES or Path(leaf).suffix in PRIVATE_SUFFIXES:
        return True
    if leaf.startswith(".env") and leaf not in {".env.example", ".env.template"}:
        return True
    if re.match(r"^id_(rsa|dsa|ecdsa|ed25519)(?:[._-]|$)", leaf):
        return True
    # Credential data and backups, while allowing documentation/source filenames.
    if re.search(r"(^|[._-])(credentials?|secrets?|tokens?)([._-]|$)", leaf):
        return not leaf.endswith((".md", ".py", ".sh"))
    return False


def safe_files(root):
    names = candidates(root)
    unsafe = sum(disallowed_path(name) for name in names)
    if unsafe:
        raise RuntimeError(f"Rejected {unsafe} private/generated candidate path(s); names suppressed.")
    for name in names:
        path = root / name
        if path.is_symlink() or not path.is_file() or not path.resolve().is_relative_to(root.resolve()):
            raise RuntimeError("Candidate contains a missing file, symlink, or unsupported entry; names suppressed.")
    return names


def png_dimensions(raw):
    """Accept bounded RGB/RGBA screenshots with no metadata or trailing payloads."""
    if len(raw) > MAX_PNG_BYTES or not raw.startswith(PNG_SIGNATURE):
        raise ValueError("Unsupported PNG.")
    offset, dimensions, channels, ended = 8, None, None, False
    image_data = bytearray()
    while offset < len(raw):
        if len(raw) - offset < 12:
            raise ValueError("Incomplete PNG chunk.")
        length = struct.unpack_from(">I", raw, offset)[0]
        kind = raw[offset + 4:offset + 8]
        end = offset + 12 + length
        if end > len(raw) or kind not in {b"IHDR", b"IDAT", b"IEND"}:
            raise ValueError("Unsupported PNG chunk.")
        body = raw[offset + 8:end - 4]
        checksum = struct.unpack_from(">I", raw, end - 4)[0]
        if zlib.crc32(kind + body) & 0xFFFFFFFF != checksum:
            raise ValueError("Invalid PNG checksum.")
        if kind == b"IHDR":
            if offset != 8 or dimensions is not None or length != 13:
                raise ValueError("Invalid PNG header.")
            width, height, depth, color, compression, filtering, interlace = struct.unpack(">IIBBBBB", body)
            if not (64 <= width <= 4096 and 64 <= height <= 4096):
                raise ValueError("Unsupported PNG dimensions.")
            if depth != 8 or color not in {2, 6} or compression or filtering or interlace:
                raise ValueError("Unsupported PNG encoding.")
            dimensions, channels = (width, height), 3 if color == 2 else 4
        elif kind == b"IDAT":
            if dimensions is None:
                raise ValueError("Missing PNG header.")
            image_data.extend(body)
        else:
            if length or not image_data or end != len(raw):
                raise ValueError("Invalid PNG ending.")
            ended = True
        offset = end
    if not ended or dimensions is None:
        raise ValueError("Incomplete PNG.")
    # A bounded inflate also rejects compressed tails and oversized hidden data.
    width, height = dimensions
    stride = width * channels + 1
    expected = stride * height
    decoder = zlib.decompressobj()
    pixels = decoder.decompress(image_data, expected + 1)
    if len(pixels) != expected or not decoder.eof or decoder.unused_data or decoder.unconsumed_tail:
        raise ValueError("Invalid PNG raster.")
    if any(pixels[row * stride] > 4 for row in range(height)):
        raise ValueError("Invalid PNG filter.")
    return dimensions


def media_problems(files):
    """Validate a working or staged media snapshot without displaying its contents."""
    pngs = {name for name in files if name.lower().endswith(".png")}
    if not pngs and MEDIA_MANIFEST not in files:
        return []
    try:
        manifest = json.loads(files[MEDIA_MANIFEST])
        if set(manifest) != {"schema_version", "assets"}:
            raise ValueError("Invalid manifest fields.")
        entries = manifest["assets"]
        if manifest["schema_version"] != "factorio-bench.public-media.v1" or not isinstance(entries, list):
            raise ValueError("Unsupported manifest.")
        if not 1 <= len(entries) <= len(PUBLIC_PNGS):
            raise ValueError("Invalid manifest size.")
        listed = set()
        fields = {"path", "sha256", "width", "height", "provenance", "reviewed"}
        for entry in entries:
            if not isinstance(entry, dict) or set(entry) != fields:
                raise ValueError("Invalid asset fields.")
            name = entry["path"]
            if name not in PUBLIC_PNGS or name in listed or entry["reviewed"] is not True:
                raise ValueError("Unreviewed or unsupported asset.")
            listed.add(name)
            provenance = entry["provenance"]
            if not isinstance(provenance, str) or not 20 <= len(provenance) <= 500:
                raise ValueError("Missing asset provenance.")
            if any(type(entry[key]) is not int for key in ("width", "height")):
                raise ValueError("Invalid declared dimensions.")
            digest = entry["sha256"]
            if not isinstance(digest, str) or not re.fullmatch(r"[0-9a-f]{64}", digest):
                raise ValueError("Invalid asset digest.")
            raw = files[name]
            if hashlib.sha256(raw).hexdigest() != digest:
                raise ValueError("Asset changed since review.")
            if png_dimensions(raw) != (entry["width"], entry["height"]):
                raise ValueError("Asset dimensions do not match manifest.")
        if listed != pngs:
            raise ValueError("Manifest does not match candidate media.")
    except (KeyError, TypeError, ValueError, UnicodeError, zlib.error):
        return ["Public media violates its reviewed PNG manifest or publication policy; details suppressed."]
    return []


def indexed_media(root):
    """Read exact indexed media so a working-tree replacement cannot hide it."""
    files = {}
    for record in git(root, "ls-files", "--stage", "-z").split(b"\0"):
        if not record:
            continue
        metadata, encoded_name = record.split(b"\t", 1)
        name = encoded_name.decode("utf-8")
        if name != MEDIA_MANIFEST and not name.lower().endswith(".png"):
            continue
        mode, oid, stage = metadata.split()
        if mode not in {b"100644", b"100755"} or stage != b"0":
            raise RuntimeError("Unsupported media index entry.")
        files[name] = git(root, "cat-file", "blob", oid.decode("ascii"))
    return files


def json_problem(value):
    """Check the task example's declared timing relationships, not fixed targets."""
    if not isinstance(value, dict) or not str(value.get("schema_version", "")).startswith("factorio-bench.task."):
        return None
    try:
        objective, clock = value["objective"], value["clock"]
        start, end = objective["evaluation_start_tick"], objective["evaluation_end_tick"]
        window, count = objective["window_ticks"], objective["window_count"]
        budget = clock["simulation_tick_budget"]
        if any(type(item) is not int for item in (start, end, window, count, budget)):
            return "task timing fields must be integers"
        if start < 0 or window <= 0 or count <= 0 or end != start + window * count:
            return "task verification windows do not match their declared interval"
        if end > budget or (value.get("termination_policy") == "fixed-horizon-with-voluntary-handoff" and end != budget):
            return "task verification interval does not match its simulation budget"
    except (KeyError, TypeError):
        return "task example lacks required timing fields"
    return None


def markdown_problems(root, name, content):
    problems = []
    fence = None
    language = ""
    block = []
    prose = []
    for line in content.splitlines():
        marker = re.match(r"^\s{0,3}(`{3,}|~{3,})(.*)$", line)
        if marker:
            run, info = marker.groups()
            if fence is None:
                fence, language, block = run, info.strip().lower(), []
                continue
            if run[0] == fence[0] and len(run) >= len(fence) and not info.strip():
                if language == "json":
                    try:
                        problem = json_problem(json.loads("\n".join(block)))
                        if problem:
                            problems.append(problem)
                    except json.JSONDecodeError:
                        problems.append("invalid fenced JSON example")
                fence = None
                continue
        if fence:
            block.append(line)
        else:
            prose.append(line)
    if fence:
        problems.append("unclosed Markdown fence")
    text = "\n".join(prose)
    # Inline and reference destinations. External links are reviewed separately.
    targets = re.findall(r"!?\[[^\]\n]*\]\(\s*(<[^>]+>|[^\s)]+)(?:\s+[^)]*)?\)", text)
    targets += re.findall(r"^\s{0,3}\[[^\]]+\]:\s*(<[^>]+>|\S+)", text, re.MULTILINE)
    for target in targets:
        parsed = urlsplit(target.strip("<>"))
        if parsed.scheme or parsed.netloc or not parsed.path:
            continue
        decoded = unquote(parsed.path)
        if decoded.startswith("/"):
            problems.append("local Markdown link must be repository-relative")
            continue
        destination = (root / name).parent / decoded
        if not destination.resolve().is_relative_to(root.resolve()) or not destination.exists():
            problems.append("local Markdown link points outside the repository or to a missing file")
    return problems


def check(root=ROOT):
    problems = []
    names = safe_files(root)
    media = {}
    for name in names:
        raw = (root / name).read_bytes()
        if name == MEDIA_MANIFEST or name.lower().endswith(".png"):
            media[name] = raw
        if name.lower().endswith(".png"):
            continue
        try:
            content = raw.decode("utf-8")
        except UnicodeDecodeError:
            problems.append("Non-text candidate requires an explicit publication policy.")
            continue
        if raw and not raw.endswith(b"\n"):
            problems.append("Text file lacks a final newline.")
        if raw.endswith(b"\n\n"):
            problems.append("Text file contains extra blank lines at end of file.")
        if "\r" in content or any(line.rstrip(" \t") != line for line in content.splitlines()):
            problems.append("Text file contains CRLF or trailing whitespace.")
        if name.endswith(".md"):
            problems.extend(markdown_problems(root, name, content))
    problems.extend(media_problems(media))
    problems.extend(media_problems(indexed_media(root)))
    if problems:
        for problem in sorted(set(problems)):
            print(f"FAIL: {problem}", file=sys.stderr)
        return 1
    print(f"Repository checks passed ({len(names)} candidate files).")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(check())
    except (OSError, RuntimeError, UnicodeError, ValueError):
        print("Repository check failed: private/unsupported candidates or inspection error; details suppressed.", file=sys.stderr)
        sys.exit(1)
