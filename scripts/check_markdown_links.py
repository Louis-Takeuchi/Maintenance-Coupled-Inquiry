#!/usr/bin/env python3
"""Check relative Markdown links in the selected public tree."""

from __future__ import annotations

import re
from pathlib import Path
from urllib.parse import unquote


ROOT = Path(__file__).resolve().parents[1]
SKIP_DIRS = {".git", "build", ".venv", "公開用再現パッケージ_v1_0_2026-08-05"}
LINK = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")


def public_markdown_files() -> list[Path]:
    output = []
    for path in ROOT.rglob("*.md"):
        relative = path.relative_to(ROOT)
        if any(part in SKIP_DIRS for part in relative.parts):
            continue
        if relative.parts and relative.parts[0] in {
            "Constitutive Inquiry MVP",
            "Constitutive Inquiry MVP docs",
            "PaperB_all_current_artifacts_2026-08-04_v0_5",
        }:
            continue
        output.append(path)
    return sorted(output)


def main() -> None:
    failures = []
    checked = 0
    for markdown in public_markdown_files():
        text = markdown.read_text(encoding="utf-8")
        for raw_target in LINK.findall(text):
            target = raw_target.strip().split(maxsplit=1)[0].strip("<>")
            if not target or target.startswith(("#", "http://", "https://", "mailto:")):
                continue
            path_part = unquote(target.split("#", 1)[0].split("?", 1)[0])
            if not path_part:
                continue
            checked += 1
            resolved = (markdown.parent / path_part).resolve()
            try:
                resolved.relative_to(ROOT.resolve())
            except ValueError:
                failures.append(f"{markdown.relative_to(ROOT)} -> outside repository: {target}")
                continue
            if not resolved.exists():
                failures.append(f"{markdown.relative_to(ROOT)} -> missing: {target}")
    if failures:
        raise SystemExit("FAIL relative links\n" + "\n".join(failures))
    print(f"PASS relative Markdown links: {checked} checked")


if __name__ == "__main__":
    main()

