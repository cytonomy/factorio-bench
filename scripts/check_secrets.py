#!/usr/bin/env python3
"""Scan history, exact index, and prospective files without printing findings."""

import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from repo_checks import ROOT, git, safe_files


def scan(command, env):
    """Do not forward stdout/stderr: even scanner errors can quote file contents."""
    result = subprocess.run(command, env=env, capture_output=True, timeout=300, check=False)
    return result.returncode == 0


def snapshot_index(root, destination):
    for record in git(root, "ls-files", "--stage", "-z").split(b"\0"):
        if not record:
            continue
        metadata, encoded_name = record.split(b"\t", 1)
        mode, oid, stage = metadata.split()
        if mode not in {b"100644", b"100755"} or stage != b"0":
            raise RuntimeError("Unsupported or unresolved index entry.")
        path = destination / encoded_name.decode("utf-8")
        if not path.resolve().is_relative_to(destination.resolve()):
            raise RuntimeError("Invalid index path.")
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(git(root, "cat-file", "blob", oid.decode("ascii")))


def check(root=ROOT):
    executable = shutil.which("gitleaks")
    if not executable:
        print("Secret checks require Gitleaks 8.30.1 or newer on PATH; no scan was completed.", file=sys.stderr)
        return 1
    names = safe_files(root)
    if git(root, "rev-parse", "--is-shallow-repository").strip() != b"false":
        print("Secret checks require complete Git history; fetch full history first.", file=sys.stderr)
        return 1
    # Explicit default rules and empty ignore file prevent environment/config bypasses.
    env = {key: value for key, value in os.environ.items() if not key.startswith("GITLEAKS_")}
    with tempfile.TemporaryDirectory(prefix="factorio-bench-scan-") as temporary:
        work = Path(temporary)
        config = work / "rules.toml"
        config.write_text("[extend]\nuseDefault = true\n", encoding="utf-8")
        ignore = work / "empty-ignore"
        ignore.write_text("", encoding="utf-8")
        index, prospective = work / "index", work / "prospective"
        index.mkdir()
        prospective.mkdir()
        snapshot_index(root, index)
        for name in names:
            destination = prospective / name
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes((root / name).read_bytes())
        common = [
            "--redact=100", "--no-banner", "--no-color", "--log-level=error",
            "--ignore-gitleaks-allow", "--gitleaks-ignore-path", str(ignore),
            "--config", str(config), "--max-decode-depth=5", "--timeout=240",
        ]
        checks = [
            ("reachable history", [executable, "git", str(root), "--log-opts=--all --full-history", *common]),
            ("exact index", [executable, "dir", str(index), *common]),
            ("prospective files", [executable, "dir", str(prospective), *common]),
        ]
        passed = True
        for label, command in checks:
            if scan(command, env):
                print(f"Secret scan passed: {label}.")
            else:
                passed = False
                print(f"Secret scan failed: {label}; findings or scanner error suppressed. Do not publish.", file=sys.stderr)
        return 0 if passed else 1


if __name__ == "__main__":
    try:
        sys.exit(check())
    except (OSError, RuntimeError, UnicodeError, ValueError, subprocess.TimeoutExpired):
        print("Secret checks could not complete safely; diagnostic output suppressed. Do not publish.", file=sys.stderr)
        sys.exit(1)
