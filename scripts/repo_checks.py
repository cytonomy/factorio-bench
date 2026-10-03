#!/usr/bin/env python3
"""Small, dependency-free checks for this documentation-first repository."""

import json
import re
import subprocess
import sys
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
    for name in names:
        raw = (root / name).read_bytes()
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
