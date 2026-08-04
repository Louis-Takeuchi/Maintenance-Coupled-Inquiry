from __future__ import annotations

import argparse
import csv
from pathlib import Path

from constitutive_inquiry.chunking import write_csv_rows
from constitutive_inquiry.development_analysis import paired_contrasts


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create paired development contrasts for Paper B.")
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--left", default="actual_need")
    parser.add_argument("--right", default="yoked_need")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    rows = read_rows(Path(args.input))
    pairs, summaries = paired_contrasts(rows, args.left, args.right)
    output = Path(args.output)
    write_csv_rows(output / "paired_contrasts.csv", pairs)
    write_csv_rows(output / "paired_summary.csv", summaries)
    print(f"wrote {len(pairs)} paired metric rows and {len(summaries)} summaries")


if __name__ == "__main__":
    main()
