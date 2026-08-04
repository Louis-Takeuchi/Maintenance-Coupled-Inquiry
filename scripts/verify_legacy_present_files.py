#!/usr/bin/env python3
"""Verify present v0.14 files while reporting intentionally excluded caches."""

from __future__ import annotations

import hashlib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LEGACY = ROOT / "legacy/constitutive_inquiry_mvp_v0_14"
MANIFEST = LEGACY / "SHA256SUMS.txt"


def is_excluded_cache(relative: str) -> bool:
    path = Path(relative.removeprefix("./"))
    return (
        ".pytest_cache" in path.parts
        or "__pycache__" in path.parts
        or path.suffix == ".pyc"
    )


def main() -> None:
    verified = 0
    excluded = []
    failures = []
    for line in MANIFEST.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        expected, relative = line.split(maxsplit=1)
        relative = relative.lstrip("*")
        path = LEGACY / relative
        if not path.exists():
            if is_excluded_cache(relative):
                excluded.append(relative)
            else:
                failures.append(f"unexpected missing file: {relative}")
            continue
        actual = hashlib.sha256(path.read_bytes()).hexdigest()
        if actual != expected:
            failures.append(f"hash mismatch: {relative}")
        else:
            verified += 1
    if failures:
        raise SystemExit("FAIL legacy verification\n" + "\n".join(failures))
    print(f"PASS legacy present-file hashes: {verified}")
    print(f"WARN stale cache entries absent by design: {len(excluded)}")
    for relative in excluded:
        print(f"  {relative}")


if __name__ == "__main__":
    main()

